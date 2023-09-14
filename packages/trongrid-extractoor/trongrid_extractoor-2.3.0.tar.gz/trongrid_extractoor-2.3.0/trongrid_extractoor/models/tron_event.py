"""
Dataclass representing one TRC20 token transfer.
"""
from dataclasses import dataclass, fields
from typing import Any, Dict, List, Optional, Tuple, Union

import pendulum

from trongrid_extractoor.config import log
from trongrid_extractoor.helpers.address_helpers import hex_to_tron
from trongrid_extractoor.helpers.rich_helpers import console
from trongrid_extractoor.helpers.string_constants import DATA, RESULT
from trongrid_extractoor.helpers.time_helpers import ms_to_datetime


@dataclass(kw_only=True)
class TronEvent:
    event_name: str
    token_address: str  # Should be contract_address
    transaction_id: str
    event_index: int
    ms_from_epoch: int
    raw_event: Optional[Dict[str, Union[str, float, int]]] = None
    block_number: Optional[int] = None

    def __post_init__(self):
        # Type coercion
        self.block_number = int(self.block_number) if self.block_number else None
        self.ms_from_epoch = int(float(self.ms_from_epoch))
        self.event_index = int(self.event_index)

        # Computed fields
        self.seconds_from_epoch = int(self.ms_from_epoch / 1000.0)
        self.datetime = pendulum.from_timestamp(self.seconds_from_epoch, pendulum.tz.UTC)
        self.unique_id = f"{self.transaction_id}/{self.event_index}"

    @classmethod
    def from_event_dict(cls, row: Dict[str, Union[str, float, int]]) -> 'TronEvent':
        """Build an event from the json data returned by Trongrid."""
        return cls(
            event_name=row['event_name'],
            token_address=row['contract_address'],
            ms_from_epoch=row['block_timestamp'],
            block_number=row['block_number'],
            transaction_id=row['transaction_id'],
            event_index=row['event_index'],
            raw_event=row
        )

    @classmethod
    def extract_from_events(cls, events: dict[str, Any]) -> List['TronEvent']:
        """Extract transfers from events."""
        try:
            tron_events = [cls.from_event_dict(row) for row in events[DATA]]
        except Exception:
            console.print_exception(show_locals=True)
            raise

        log.debug(f"Extracted {len(tron_events)} txns from the response...")
        return tron_events

    def __str__(self) -> str:
        msg = f"Event: {self.token_address[0:10]}..., , ID: {self.transaction_id[0:10]}.../{self.event_index}"
        return msg + f", Amount: {self.amount} (at {self.datetime})"
