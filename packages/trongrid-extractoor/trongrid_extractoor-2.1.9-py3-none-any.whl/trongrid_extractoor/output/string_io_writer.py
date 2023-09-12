"""
Writer to a StringIO
  - Trc20Txns are written as CSVs
  - TronEvents are written as JSON
"""
import csv
from io import StringIO
from typing import List, Type

from trongrid_extractoor.helpers.address_helpers import *
from trongrid_extractoor.models.trc20_txn import Trc20Txn
from trongrid_extractoor.models.tron_event import TronEvent
from trongrid_extractoor.output.output_writer import OutputWriter


class StringIOWriter(OutputWriter):
    def __init__(self, output_io: StringIO, output_cls: Type) -> None:
        super().__init__(output_cls)
        self.output_io = output_io
        self.file_mode = 'w'

    def write_txns(self, rows: List[Trc20Txn]) -> None:
        self._write_txns(rows, self.output_io)

    def write_json(self, rows: List[TronEvent]) -> None:
        self._write_json(rows, self.output_io)
