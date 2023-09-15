"""
Dataclass representing an account at Tron/and or Tronscan.
"""
from copy import deepcopy
from dataclasses import dataclass
from typing import Dict, Optional, Union

from rich.panel import Panel
from rich.pretty import pprint
from rich.text import Text

from trongrid_extractoor.helpers.string_constants import (ABI, ACCOUNT_NAME, ADDRESS, NAME, BALANCE, TYPE)

# This is a huge string in the JSON.
KEYS_TO_SUPPRESS_IN_LOGS = ['bytecode']


@dataclass(kw_only=True)
class TronContract():
    address: str
    name: Optional[str]
    abi: Optional[Dict[str, any]]
    origin_address: Optional[str]
    raw_json: Optional[Dict[str, Union[dict, str, float, int]]] = None

    @classmethod
    def from_response_dict(cls, contract: Dict[str, Union[dict, str, float, int]]) -> 'TronContract':
        """Build a TronContract from the json data returned by Trongrid."""
        try:
            return cls(
                address=contract['contract_address'],
                abi=contract.get(ABI),
                name=contract.get(NAME),
                origin_address=contract.get('origin_address'),
                raw_json=contract
            )
        except KeyError:
            pprint(contract, expand_all=True)
            raise

    def label(self) -> str:
        return f"Contract: {self.name}" if self.name else '[AnonymousContract]'

    # def child_contract_label(self) -> str:
    #     """String to be used in the labeling of contracts deployed by this contract."""
    #     if self.name:
    #         return f"Deployed by Contract: {self.name} ({self.address})"
    #     else:
    #         return f"Deployed by [AnonymousContract: {self.address}]"

    def raw_dict_shortened(self) -> Optional[Dict[str, Union[dict, str, float, int]]]:
        raw_copy = deepcopy(self.raw_json)

        for key in KEYS_TO_SUPPRESS_IN_LOGS:
            if key not in raw_copy:
                continue

            if key == 'bytecode':
                raw_copy[key] = '[REDACTED_FOR_BREVITY]'
            else:
                raw_copy[key] = [f"(List containing {len(raw_copy[key])} elements removed)"]

        return raw_copy

    def __rich__(self) -> Panel:
        txt = Text('').append(self.address, style='bright_cyan')

        if self.name:
            txt.append(f" ({self.name})")

        return Panel(txt, expand=False)
