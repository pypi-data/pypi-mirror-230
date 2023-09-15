"""
Writer to a file.
  - Trc20Txns are written as CSVs
  - TronEvents are written as JSON
"""
from pathlib import Path
from typing import List, Union, Type

from trongrid_extractoor.helpers.address_helpers import *
from trongrid_extractoor.models.trc20_txn import Trc20Txn
from trongrid_extractoor.models.tron_event import TronEvent
from trongrid_extractoor.output.output_writer import OutputWriter


class FileOutputWriter(OutputWriter):
    def __init__(self, output_path: Union[str, Path], output_cls: Type) -> None:
        super().__init__(output_cls)
        self.output_path = Path(output_path)
        self.file_mode = 'a' if self.output_path.exists() else 'w'

        if output_cls == TronEvent:
            self.output_path = self.output_path.with_suffix('.json')

    def write_txns(self, rows: List[Trc20Txn]) -> None:
        with open(self.output_path, self.file_mode) as output_file:
            self._write_txns(rows, output_file)

    def write_json(self, rows: List[TronEvent]) -> None:
        with open(self.output_path, self.file_mode) as output_file:
            self._write_json(rows, output_file)
