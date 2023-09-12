"""
Class to track with transactions we've already seen and the CSV to write to.
"""
import csv
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from sys import exit

from pendulum import DateTime
from rich.text import Text

from trongrid_extractoor.config import log
from trongrid_extractoor.helpers.rich_helpers import print_error_and_exit
from trongrid_extractoor.helpers.string_constants import TRANSFER
from trongrid_extractoor.helpers.time_helpers import ms_to_datetime
from trongrid_extractoor.models.trc20_txn import Trc20Txn
from trongrid_extractoor.models.tron_event import TronEvent


class ProgressTracker:
    def __init__(
            self,
            contract_address: Optional[str] = None,
            resume_from_csv: Optional[Path] = None
        ) -> None:
        if contract_address is None and resume_from_csv is None:
            raise ValueError(f"No contract_address provded and no file to resume from.")

        self.contract_address = contract_address
        self.already_processed_uniq_ids = set()
        self.earliest_timestamp_seen_ms = None
        self.latest_timestamp_seen_ms = None
        self.min_block_number_seen = None
        self.max_block_number_seen = None
        self.rows_in_scanned_csv = 0

        # Resume from CSV if requested
        if resume_from_csv:
            self._load_csv_progress(resume_from_csv)

    def remove_already_processed_txns(self, txns: List[TronEvent]) -> List[TronEvent]:
        """
        Track already seen unique_ids ("transaction_id/event_index") and the earliest block_timestamp
        encountered. Remove any transactions w/IDs return the resulting list.
        """
        filtered_txns = []

        for txn in txns:
            if txn.unique_id in self.already_processed_uniq_ids:
                log.warning(f"Already processed: {txn}")
                continue

            if self.earliest_timestamp_seen_ms is None or txn.ms_from_epoch < self.earliest_timestamp_seen_ms:
                self.earliest_timestamp_seen_ms = txn.ms_from_epoch
            if self.latest_timestamp_seen_ms is None or txn.ms_from_epoch > self.latest_timestamp_seen_ms:
                self.latest_timestamp_seen_ms = txn.ms_from_epoch
            if self.min_block_number_seen is None or txn.block_number < self.min_block_number_seen:
                self.min_block_number_seen = txn.block_number
            if self.max_block_number_seen is None or txn.block_number > self.max_block_number_seen:
                self.max_block_number_seen = txn.block_number

            filtered_txns.append(txn)
            self.already_processed_uniq_ids.add(txn.unique_id)

        removed_txn_count = len(txns) - len(filtered_txns)

        if removed_txn_count > 0:
            log.warning(f"  Removed {removed_txn_count} duplicate transactions...")

        return filtered_txns

    def earliest_timestamp_seen(self) -> Optional[DateTime]:
        """Convert the milliseconds to a DateTime."""
        if self.earliest_timestamp_seen_ms:
            return ms_to_datetime(self.earliest_timestamp_seen_ms)

    def latest_timestamp_seen(self) -> Optional[DateTime]:
        """Convert the milliseconds to a DateTime."""
        if self.latest_timestamp_seen_ms:
            return ms_to_datetime(self.latest_timestamp_seen_ms)

    def number_of_rows_written(self) -> int:
        return len(self.already_processed_uniq_ids) - self.rows_in_scanned_csv

    def _load_csv_progress(self, resume_from_csv: Path) -> None:
        """Read a CSV and consider each row as having already been processed."""
        if not resume_from_csv.exists():
            raise ValueError(f"Can't resume from CSV because '{resume_from_csv}' doesn't exist!")

        with open(resume_from_csv, mode='r') as csvfile:
            for row in csv.DictReader(csvfile, delimiter=','):
                self.remove_already_processed_txns([Trc20Txn(**{'event_name': TRANSFER, **row})])
                row_contract_address = row['token_address']

                if self.contract_address is None:
                    self.contract_address = row_contract_address
                    log.info(f"Found token address '{self.contract_address}' in CSV...")
                elif self.contract_address != row_contract_address:
                    msg = f"CSV contains data for '{row_contract_address}' but '{self.contract_address}' given as --token arg."
                    print_error_and_exit(msg)

                self.rows_in_scanned_csv += 1

        log.info(f"Processed {self.rows_in_scanned_csv} rows in '{resume_from_csv}',")
        log.info(f"   Resuming from {self.earliest_timestamp_seen()}.")
