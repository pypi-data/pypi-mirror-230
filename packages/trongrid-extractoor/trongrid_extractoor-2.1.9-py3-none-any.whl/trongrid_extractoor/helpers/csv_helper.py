"""
Manager writing to either StringIO or to a CSV file.
  - Trc20Txns are written as CSVs
  - TronEvents are written as JSON
"""
import csv
import json
import re
from abc import abstractmethod
from datetime import datetime
from io import StringIO, TextIOBase
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import pendulum
from rich.pretty import pprint

from trongrid_extractoor.config import log
from trongrid_extractoor.helpers.address_helpers import *
from trongrid_extractoor.models.trc20_txn import CSV_FIELDS, Trc20Txn
from trongrid_extractoor.models.tron_event import TronEvent

WRITTEN = 'written'
WRITTEN_AT_REGEX = re.compile(WRITTEN + "_(\\d{4}-\\d{2}-\\d{2}T\\d{2}[.:]\\d{2}[.:]\\d{2})\\.csv")


def read_json(file_path: Path) -> List[Dict[str, Any]]:
    """JSON is dumped as a series of arrays so we need to turn the string into a single array."""
    with open(file_path, 'r') as file:
        return json.loads(file.read().replace('][', ','))


def output_csv_path(address: str, dir: Optional[Path] = None, suffix: Optional[str] = None) -> Path:
    """
    Build a filename that contains the address and (if available) the symbol.
    Suffix is an optional string to be passed in by the user when used as a package.
    """
    dir = dir or Path('')
    filename = csv_prefix(address)

    if suffix:
        filename += f"__{suffix}"

    # TODO: stop replacing the ':'
    filename += csv_suffix()
    return dir.joinpath(filename.replace(':', '.').replace('/', '.'))


def load_csv(csv_path: Union[str, Path]) -> List[Dict[str, Any]]:
    with open(Path(csv_path), mode='r') as csvfile:
        return [
            row
            for row in csv.DictReader(csvfile, delimiter=',')
        ]


def csvs_with_prefix_in_dir(dir: Union[str, Path], prefix: str) -> List[str]:
    return [f.name for f in Path(dir).glob(f"{prefix}*.csv")]


def csv_prefix(address: str) -> str:
    filename = 'events_'

    if is_contract_address(address):
        symbol = symbol_for_address(address)
    else:
        symbol = address
        address = address_of_symbol(address)

        if not address:
            raise ValueError(f"No address found for {symbol}!")

    if symbol:
        filename += f"{symbol}_"

    filename += address
    return filename


def csv_suffix() -> str:
    """String showing the time the file was created."""
    return f"__{WRITTEN}_{datetime.now().strftime('%Y-%m-%dT%H.%M.%S')}.csv"


def parse_written_at_from_filename(csv_path: Union[str, Path]) -> pendulum.DateTime:
    """Extract the written timestmap (output of csv_suffix()) to a timestamp."""
    match = WRITTEN_AT_REGEX.search(str(csv_path))

    if match is None:
        raise ValueError(f"'{csv_path}' does not seem to have an embedded written_at timestamp!")

    return pendulum.parse(match.group(1).replace('.', ':'))
