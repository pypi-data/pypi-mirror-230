"""
Class to build HTTP request params for Trongrid API endpoints.
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union

import pendulum
from pendulum import DateTime

from trongrid_extractoor.config import log
from trongrid_extractoor.helpers.string_constants import EVENT_NAME, MIN_TIMESTAMP, MAX_TIMESTAMP, TRANSFER
from trongrid_extractoor.helpers.time_helpers import TRON_LAUNCH_TIME, datetime_to_ms, ms_to_datetime

ParamsType = Dict[str, Union[str, int, float]]

DEFAULT_MAX_TIMESTAMP = pendulum.now('UTC').add(months=2)
MAX_TRADES_PER_CALL = 200


@dataclass
class EventRequestParams:
    contract_url: str
    min_timestamp: Optional[DateTime] = TRON_LAUNCH_TIME
    max_timestamp: Optional[DateTime] = DEFAULT_MAX_TIMESTAMP
    extra: Dict[str, Any] = field(default_factory=dict)
    event_name: Optional[str] = TRANSFER

    def __post_init__(self):
        self.min_timestamp = self.min_timestamp or TRON_LAUNCH_TIME
        self.max_timestamp = self.max_timestamp or DEFAULT_MAX_TIMESTAMP
        log.info(f"Request URL: {self.contract_url}\n{self}")

    def request_params(self) -> Dict[str, Union[str, int, float]]:
        """Build the actual params for the POST request."""
        params = {
            'only_confirmed': 'true',
            'limit': MAX_TRADES_PER_CALL,
            MIN_TIMESTAMP: datetime_to_ms(self.min_timestamp),
            MAX_TIMESTAMP: datetime_to_ms(self.max_timestamp)
        }

        if self.event_name is not None:
            params[EVENT_NAME] = self.event_name

        return {**params, **self.extra}

    def __str__(self) -> str:
        event_name = 'all' if self.event_name is None else f"'{self.event_name}'"
        msg = f"Params requesting {event_name} events from {self.min_timestamp} to {self.max_timestamp}"

        if len(self.extra) == 0:
            return msg + f" (no extra params)."
        else:
            return msg + f", extra params: {self.extra}"

    @staticmethod
    def is_new_query(params: ParamsType):
        """
        If an API call yields too many rows to fit in one response a 'next URL' is given and
        our requests use that URL without params, ergo only new queries have MIN/MAX_TIMESTAMP.
        """
        return (MIN_TIMESTAMP in params) and (MAX_TIMESTAMP in params)

    @staticmethod
    def timespan_string(params: ParamsType):
        """Human readable string showing the from/to datetime requested by 'params'."""
        return f"from {ms_to_datetime(params[MIN_TIMESTAMP])} to {ms_to_datetime(params[MAX_TIMESTAMP])}"
