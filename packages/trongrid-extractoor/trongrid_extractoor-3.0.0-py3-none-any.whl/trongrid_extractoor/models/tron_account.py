"""
Dataclass representing an account at Tron/and or Tronscan.
"""
from copy import deepcopy
from dataclasses import dataclass
from typing import Dict, Optional, Union

from rich.panel import Panel
from rich.text import Text

from trongrid_extractoor.helpers.string_constants import (ACCOUNT_NAME, ADDRESS, BALANCE, CONTRACT, TYPE)

# In the JSON responses these are huge arrays of dicts.
KEYS_TO_SUPPRESS_IN_LOGS = ['assetV2', 'free_asset_net_usageV2']


@dataclass(kw_only=True)
class TronAccount():
    address: str
    name: Optional[str]
    account_type: Optional[str]
    trx_balance: Optional[int]
    raw_json: Optional[Dict[str, Union[dict, str, float, int]]] = None

    def __post_init__(self):
        self.trx_balance = int(self.trx_balance) if self.trx_balance is not None else None

    @classmethod
    def from_response_dict(cls, account: Dict[str, Union[str, float, int]], api: 'Api') -> 'TronAccount':
        """Build an event from the json data returned by Trongrid."""
        tron_account = cls(
            address=account[ADDRESS],
            name=account.get(ACCOUNT_NAME),
            account_type=account.get(TYPE),
            trx_balance=account.get(BALANCE),
            raw_json=account
        )

        # If it's a contract, find out more about who deployed it.
        if tron_account.account_type and tron_account.account_type.lower() == CONTRACT:
            contract = api.get_contract(tron_account.address)

            if tron_account.name is not None:
                tron_account.name = f"Contract: {tron_account.name}"
            else:
                tron_account.name = contract.label()

            creator_account = api.get_account(contract.origin_address)

            if creator_account:
                tron_account.name += f" [Deployed by "

                if creator_account.name:
                    tron_account.name += f"{creator_account.name} @ {creator_account.address}"
                else:
                    tron_account.name += f"{creator_account.address}"

                tron_account.name += ']'

        return tron_account

    def raw_dict_shortened(self) -> Optional[Dict[str, Union[dict, str, float, int]]]:
        raw_copy = deepcopy(self.raw_json)

        for key in KEYS_TO_SUPPRESS_IN_LOGS:
            if key not in raw_copy:
                continue

            raw_copy[key] = [f"(List containing {len(raw_copy[key])} elements removed)"]

        return raw_copy

    def __rich__(self) -> Panel:
        txt = Text('').append(self.account_type or '[NO_TYPE]', style='color(228)').append(': ')
        txt.append(self.address, style='bright_cyan')

        if self.name:
            txt.append(f" ({self.name})")

        return Panel(txt, expand=False)
