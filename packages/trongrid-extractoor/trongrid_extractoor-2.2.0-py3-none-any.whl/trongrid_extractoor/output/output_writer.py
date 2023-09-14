"""
Manager writing to either StringIO or to a CSV file.
  - Trc20Txns are written as CSVs
  - TronEvents are written as JSON
"""
import csv
import json
from abc import abstractmethod
from collections import defaultdict
from typing import Any, List, Type

from rich.pretty import pprint

from trongrid_extractoor.config import log
from trongrid_extractoor.helpers.address_helpers import *
from trongrid_extractoor.models.trc20_txn import CSV_FIELDS, Trc20Txn
from trongrid_extractoor.models.tron_event import TronEvent
from trongrid_extractoor.request_params import MAX_TRADES_PER_CALL
from trongrid_extractoor.helpers.string_constants import TRANSFER

LOG_INTERVAL = 10
JSON_INDENT = 3


class OutputWriter:
    def __init__(self, output_cls: Type) -> None:
        self.output_cls = output_cls
        self.lines_written = 0
        self.event_counts = defaultdict(lambda: 0)

        if self.is_writing_csv():
            self._write_fxn = self.write_txns
        else:
            self._write_fxn = self.write_json

    def write_rows(self, rows: List[Any]) -> None:
        """Write json or CSV."""
        if len(rows) == 0:
            log.warning(f"Nothing to write (0 rows)...")
            return

        self._write_fxn(rows)
        self._log_progress(rows)

    def is_writing_csv(self):
        return self.output_cls == Trc20Txn

    @abstractmethod
    def write_txns(self, rows: List[Trc20Txn]) -> None:
        pass

    @abstractmethod
    def write_json(self, rows: List[TronEvent]) -> None:
        pass

    def _write_txns(self, rows: List[Trc20Txn], writeable_io) -> None:
        """Txns are written to a CSV with particular columns."""
        csv_writer = csv.DictWriter(writeable_io, CSV_FIELDS, lineterminator='\n')

        if self.file_mode == 'w':
            csv_writer.writeheader()

        csv_writer.writerows([row.as_dict(CSV_FIELDS) for row in rows])
        self.file_mode = 'a'

    def _write_json(self, events: List[TronEvent], writeable_io) -> None:
        for event in events:
            json_string = json.dumps(event.raw_event, indent=JSON_INDENT)

            if event.event_name not in self.event_counts:
                log.info(f"New event type encountered: '{event.event_name}'")
            elif not event.event_name:
                log.warning(f"Unnamed event!")
                console.print_json(json_string)

            # Insert commas between json dicts
            if self.file_mode == 'a':
                writeable_io.write(',')

            json.dump(event.raw_event, writeable_io, indent=JSON_INDENT)
            self.event_counts[event.event_name] += 1
            self.file_mode = 'a'

    def _log_progress(self, rows: List[TronEvent]) -> None:
        self.lines_written += len(rows)
        log.info(f"Wrote {len(rows)} rows ({self.lines_written} total)...")

        if int(self.lines_written / MAX_TRADES_PER_CALL) % LOG_INTERVAL != 0:
            return

        log.info(f"  Timestamp of last row: {rows[0].datetime}")

        if len(self.event_counts) > 1:
            log.info(f"Event counts so far:")
            pprint(dict(self.event_counts), expand_all=True)
