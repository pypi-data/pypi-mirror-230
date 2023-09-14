'''
API wrapper for TronGrid.
'''
import os
import tempfile
from io import StringIO
from pathlib import Path
from typing import Any, Dict, List, Optional, Type, Union

import pendulum
from pendulum import DateTime

from trongrid_extractoor.config import log
from trongrid_extractoor.helpers.address_helpers import coerce_to_base58, coerce_to_hex, is_tron_base58_address
from trongrid_extractoor.helpers.csv_helper import output_csv_path
from trongrid_extractoor.helpers.string_constants import *
from trongrid_extractoor.helpers.time_helpers import *
from trongrid_extractoor.models.trc20_txn import Trc20Txn
from trongrid_extractoor.models.tron_account import TronAccount
from trongrid_extractoor.models.tron_contract import TronContract
from trongrid_extractoor.models.tron_event import TronEvent
from trongrid_extractoor.output.file_output_writer import FileOutputWriter
from trongrid_extractoor.output.string_io_writer import StringIOWriter
from trongrid_extractoor.progress_tracker import ProgressTracker
from trongrid_extractoor.request_params import MAX_TRADES_PER_CALL, EventRequestParams
from trongrid_extractoor.response import Response

RESCUE_DURATION_WALKBACK_SECONDS = [
    20,
    200,
    1000,
]

ONE_SECOND_MS = 1000.0
EMPTY_RESPONSE_RETRY_AFTER_SECONDS = 60

# Currently we poll from the most recent to the earliest events which is perhaps non optimal
ORDER_BY_BLOCK_TIMESTAMP_ASC = 'block_timestamp,asc'
ORDER_BY_BLOCK_TIMESTAMP_DESC = 'block_timestamp,desc'


class Api:
    def __init__(self, network: str = MAINNET, api_key: str = '') -> None:
        network = '' if network == MAINNET else f".{network}"
        self.base_uri = f"https://api{network}.trongrid.io/"
        self.api_key = api_key

    def contract_events(
            self,
            contract_address: Optional[str] = None,
            event_name: str = 'Transfer',
            since: Optional[DateTime] = None,
            until: Optional[DateTime] = None,
            output_to: Optional[Union[Path, StringIO]] = None,
            filename_suffix: Optional[str] = None,
            resume_from_csv: Optional[Path] = None
        ) -> Path:
        """
        Get events by contract address and write to CSV. This is the endpoint that actually works
        to get all transactions (unlike the '[CONTRACT_ADDRESS]/transactions' endpoint).

          - contract_address:   On-chain address of the token
          - since:           Start time to retrieve
          - until:           Start time to retrieve
          - output_to        Either a directory to write a CSV to or a StringIO object to receive CSV
          - filename_suffix: Optional string to append to the filename
          - resume_from_csv:      Path to a CSV you want to resume writing
          - event_name:      Type of event to retrieve

        Test harness: https://developers.tron.network/v4.0/reference/events-by-contract-address
        """
        # Resume from CSV if requested
        if resume_from_csv is None and not is_tron_base58_address(contract_address):
            raise ValueError(f"Must provide a valid contract address or a CSV to resume.")

        event_cls = Trc20Txn if event_name == TRANSFER else TronEvent

        if isinstance(output_to, StringIO):
            writer = StringIOWriter(output_stream, event_cls)
            output_path = None
        else:
            if resume_from_csv is not None:
                output_path = resume_from_csv
            elif output_to is None or isinstance(output_to, (str, Path)):
                output_to = output_to or Path('')
                output_to = Path(output_to)

                if not output_to.is_dir():
                    raise ValueError(f"'{output_to}' is not a directory")

                output_path = output_csv_path(contract_address, output_to, filename_suffix)
            else:
                raise ValueError(f"output_to arg of wrong type: '{output_to}' ({type(output_to).__name__})")


            writer = FileOutputWriter(output_path, event_cls)
            log.info(f"Output CSV: '{output_path}'")

        # Setup params
        progress_tracker = ProgressTracker(contract_address, resume_from_csv)
        contract_address = contract_address or progress_tracker.contract_address
        endpoint_url = self._build_endpoint_url(f"v1/contracts/{contract_address}/events")
        params = EventRequestParams(endpoint_url, since, until, event_name=event_name)
        params.max_timestamp = progress_tracker.earliest_timestamp_seen() or params.max_timestamp

        # Start retrieving
        response = Response.get_response(endpoint_url, params.request_params())
        retrieved_txns = event_cls.extract_from_events(response.response)
        retrieved_txns = progress_tracker.remove_already_processed_txns(retrieved_txns)
        writer.write_rows(retrieved_txns)

        # Pull the next record from the provided next URL until there's nothing left to pull
        while response.is_continuable_response():
            response = Response.get_response(response.next_url())
            retrieved_txns = event_cls.extract_from_events(response.response)
            retrieved_txns = progress_tracker.remove_already_processed_txns(retrieved_txns)
            writer.write_rows(retrieved_txns)

            if response.is_paging_complete():
                log.info(f"Paging complete for {params} so will end loop...")

        log.info(f"Extraction complete. Wrote {progress_tracker.number_of_rows_written()} new rows to '{output_path}'.")
        log.info(f"    Lowest block_number seen:  {progress_tracker.min_block_number_seen}")
        log.info(f"    Highest block_number seen: {progress_tracker.max_block_number_seen}")
        log.info(f"Here is the last response from the api for {params}")
        response.print_abbreviated()
        return output_path or output_stream

    def get_contract(self, address: str, use_base58: bool = False) -> Optional[Dict[str, Any]]:
        """
        Get information about contract at a given address.
        Test harness: https://developers.tron.network/v4.0/reference/get-contract
        """
        log.info(f"Retrieving contract at '{address}'...")
        endpoint_url = self._build_endpoint_url('wallet/getcontract')
        address = coerce_to_base58(address) if use_base58 else coerce_to_hex(address)
        params = {VALUE: address, VISIBLE: use_base58}
        response = Response.post_response(endpoint_url, params).response

        # TODO: default to base58
        if len(response) > 0:
            if use_base58:
                return TronContract.from_response_dict(response)
            else:
                return response

    def get_account(self, address: str) -> Optional[TronAccount]:
        """
        Get information about an account. Things like self tags, balances, etc. Note that 'getaccount' endpoint
        only returns human readable tag information if you request info for base58 form of address with 'visible'=True args.
        Test harness: https://developers.tron.network/v4.0/reference/walletgetaccount
        """
        log.debug(f"Retrieving account at '{address}'...")
        endpoint_url = self._build_endpoint_url('wallet/getaccount')
        params = {ADDRESS: coerce_to_base58(address), VISIBLE: True}
        response = Response.post_response(endpoint_url, params).response

        if len(response) != 0:
            return TronAccount.from_response_dict(response, self)

    def _extract_events_from_response(
            self,
            response: Response,
            progress_tracker: ProgressTracker,
            event_cls: Type,
            internal_txns: bool = False,
        ) -> List[TronEvent]:
        """Build events from response."""
        if internal_txns:
            events = TronEvent.extract_from_events(response.response[DATA], internal_txns)

            events = [
                event_cls.extract_from_events(self.transaction_events(event.transaction_id)[DATA], internal_txns)
                for event in events
            ]
        else:
            events = event_cls.extract_from_events(response.response[DATA])

        return progress_tracker.remove_already_processed_txns([e for e in chain(*events)])

    def _build_endpoint_url(self, url_path: str) -> str:
        return f"{self.base_uri}{url_path}"
