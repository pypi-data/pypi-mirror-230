"""
Dataclass representing an account at Tron/and or Tronscan.
"""
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional, Tuple, Union


from trongrid_extractoor.config import log
from trongrid_extractoor.models.tron_event import TronEvent
from trongrid_extractoor.helpers.address_helpers import hex_to_tron
from trongrid_extractoor.helpers.string_constants import (ACCOUNT_NAME, ADDRESS, BALANCE, TYPE)
from trongrid_extractoor.exceptions import UnparseableResponse


@dataclass(kw_only=True)
class TronAccount():
    address: str
    account_name: Optional[str]
    account_type: Optional[str]
    trx_balance: Optional[int]
    raw_account_dict: Optional[Dict[str, Union[dict, str, float, int]]] = None

    def __post_init__(self):
        self.trx_balance = int(self.trx_balance) if self.trx_balance is not None else None

    @classmethod
    def from_event_dict(cls, account: Dict[str, Union[str, float, int]]) -> 'TronAccount':
        """Build an event from the json data returned by Trongrid."""
        return cls(
            address=account[ADDRESS],
            account_name=account.get(ACCOUNT_NAME),
            account_type=account.get(TYPE),
            trx_balance=account.get(BALANCE),
            raw_account_dict=account
        )
