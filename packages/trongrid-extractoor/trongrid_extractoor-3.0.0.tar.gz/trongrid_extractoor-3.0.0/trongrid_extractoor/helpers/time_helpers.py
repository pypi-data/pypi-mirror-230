import re
from typing import Union

import pendulum
from pendulum import DateTime

from trongrid_extractoor.config import log

# 2017-01-01, though Tron was really prolly launched in 2018
TRON_LAUNCH_TIME = pendulum.datetime(2017, 1, 1, tz='UTC')
TRON_LAUNCH_TIME_IN_EPOCH_MS = TRON_LAUNCH_TIME.timestamp() * 1000
MAX_TIME = DateTime.now().add(years=2)


def ms_to_datetime(ms: Union[float, int, str]) -> DateTime:
    """Convert epoch milliseconds to DateTime. Also work for epoch seconds as a convenience."""
    try:
        datetime = pendulum.from_timestamp(float(ms))
    except ValueError as e:
        if not re.match('year \\d+ is out of range', str(e)):
            raise e

        log.warning(f"{ms} seems like it's probably epoch milliseconds seconds not seconds...")
        datetime = pendulum.from_timestamp(float(ms) / 1000.0)

    log.debug(f"Extracted time {datetime} from {ms}")
    return datetime


def datetime_to_ms(timestamp: Union[str, DateTime]) -> float:
    if isinstance(timestamp, str):
        timestamp = timestamp if '+' in timestamp else timestamp + '+00:00'  # Add UTC if need be
        timestamp = DateTime.fromisoformat(timestamp)

    is_valid_timestamp(timestamp)
    return timestamp.timestamp() * 1000


def str_to_timestamp(iso_timestamp_string: str) -> DateTime:
    timestamp = DateTime.fromisoformat(iso_timestamp_string)

    try:
        is_valid_timestamp(timestamp)
    except TypeError as e:
        if "can't compare offset-naive and offset-aware datetimes" in str(e):
            log.warning(f"No timezone provided in '{iso_timestamp_string}'. Appending +00:00 for UTC...")
            return str_to_timestamp(iso_timestamp_string + '+00:00')

    return timestamp


def is_valid_timestamp(timestamp: DateTime) -> bool:
    if timestamp < TRON_LAUNCH_TIME:
        raise ValueError(f"{timestamp} is before {TRON_LAUNCH_TIME}!")
    elif timestamp > MAX_TIME:
        raise ValueError(f"{timestamp} is too far in the future!")

    return True
