"""
Wrapper for trongrid's response JSON data.
"""
import logging
from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Dict, Optional, Union

import requests
from requests_toolbelt.utils import dump
from rich.pretty import pprint
from tenacity import after_log, retry, stop_after_attempt, wait_exponential

from trongrid_extractoor.config import log
from trongrid_extractoor.exceptions import *
from trongrid_extractoor.helpers.string_constants import *
from trongrid_extractoor.helpers.time_helpers import *
from trongrid_extractoor.request_params import EventRequestParams, ParamsType

# If the distance between min and max_timestamp is less than this don't consider a 0 row
# result a failure.
OK_DURATION_FOR_ZERO_TXNS_MS = 10000
ABBREVIATED_RESPONSE_DATA_LENGTH = 2
JSON_HEADERS = {'Accept': JSON_MIME_TYPE}
POST_HEADERS = {'content-type': JSON_MIME_TYPE, **JSON_HEADERS}
EMPTY_RESPONSE_MSG = 'Empty response that perhaps should not be empty.'

TRONGRID_RETRY_KWARGS = {
    'wait': wait_exponential(multiplier=1, min=15, max=300),
    'stop': stop_after_attempt(5),
    'after': after_log(log, logging.DEBUG),
}


@dataclass
class Response:
    raw_response: requests.models.Response
    params: ParamsType

    def __post_init__(self):
        log.debug(dump.dump_all(self.raw_response).decode('utf-8'))
        self.response = self.raw_response.json()

    @classmethod
    @retry(**TRONGRID_RETRY_KWARGS)
    def get_response(cls, url: str, params: Optional[ParamsType] = None) -> 'Response':
        """Alternate constructor that calls the API with retries."""
        params = params or {}

        # Min/Max timestamps are INCLUSIVE.
        if EventRequestParams.is_new_query(params):
            log.info(f"Requesting data {EventRequestParams.timespan_string(params)}...")

        log.debug(f"Request URL: {url}\nParams: {params}")
        raw_response = requests.get(url, headers=JSON_HEADERS, params=params)
        response = cls(raw_response, deepcopy(params))
        response._validate()
        return response

    @classmethod
    @retry(**TRONGRID_RETRY_KWARGS)
    def post_response(cls, url: str, params: Optional[ParamsType] = None) -> 'Response':
        """Alternate constructor for use with a POST request. Doesn't validate events, just parses JSON."""
        params = params or {}
        raw_response = requests.post(url, headers=POST_HEADERS, json=params)

        if raw_response.status_code >= 400:
            log.error(dump.dump_all(raw_response).decode('utf-8'))
            raise TrongridError(f"Http {raw_response.status_code}: {raw_response.reason}")

        return cls(raw_response, deepcopy(params))

    def is_continuable_response(self) -> bool:
        """Return True if the response contains a link to the next page via a url."""
        return self.next_url() is not None

    def is_paging_complete(self) -> bool:
        """Return True if it appears that we successfully paged to the end of the query."""
        page_size = self._page_size() or 0
        return self._was_successful() and page_size > 0 and self.next_url() is None

    def next_url(self) -> Optional[str]:
        """If the number of results is more than the page size Trongrid return a URL for the next page."""
        if META in self.response and LINKS in self.response[META] and NEXT in self.response[META][LINKS]:
            return self.response[META][LINKS][NEXT]

    def pretty_print(self) -> None:
        log.info(f"RAW RESPONSE:")
        log.info(dump.dump_all(self.raw_response).decode('utf-8') + "\n")
        log.info(f"Response formatted with Rich:")
        pprint(self, expand_all=True)
        pprint(self.response, expand_all=True)

    def print_abbreviated(self) -> None:
        abbreviated_response = deepcopy(self.response)
        abbreviated_response[DATA] = abbreviated_response[DATA][:ABBREVIATED_RESPONSE_DATA_LENGTH]
        num_datapoints_not_shown = len(self.response[DATA]) - ABBREVIATED_RESPONSE_DATA_LENGTH

        if num_datapoints_not_shown > 0:
            abbreviated_response[DATA].append(f"[Skipping the other {num_datapoints_not_shown} elements of 'data' array...]")

        pprint(abbreviated_response, expand_all=True)

    def _page_size(self) -> Optional[int]:
        """Extract the number of results returned in this page of results."""
        if META in self.response and PAGE_SIZE in self.response[META]:
            return self.response[META][PAGE_SIZE]

    def _was_successful(self) -> bool:
        """Returns True if the server response was a success."""
        if SUCCESS not in self.response:
            log.warning(f"No '{SUCCESS}' key found in response!\n{self.response}")
            return False

        success = self.response[SUCCESS]

        if not isinstance(success, bool):
            raise ValueError(f"{success} is of type {type(success)} instead of bool!")

        return success

    def _validate(self):
        """Raise exception if bad response."""
        # Sometimes TronGrid will return 0 rows for no apparent reason. Retrying usually fixes it
        # so we throw an exception to get a tenacity retry.
        # It also seems that if the number of responses to a query is a multiple of 200 (the page sizez)
        # Trongrid may page through to an empty response. That case is not well handled here.
        if self._is_false_complete_response() and not EventRequestParams.is_new_query(self.params):
            msg = f"{EMPTY_RESPONSE_MSG}. Response:\n{self.response}\n\nRetrying.."
            log.warning(msg)
            self.pretty_print()
            raise IllegitimateEmptyResponseError(msg)
        elif ERROR in self.response:
            error_msg = self.response[ERROR]
            log.warning(f"Error in response: '{error_msg}'")
            self.pretty_print()

            if 'request rate exceeded' in error_msg:
                log.warning(f"Rate limit exceeded; backing off...")
                raise RateLimitExceededError(error_msg)

            raise TrongridError(error_msg)
        elif DATA not in self.response:
            log.error(dump.dump_all(self.raw_response).decode('utf-8'))
            raise TrongridError(f"No 'data' property found in {self.response}")

    def _is_false_complete_response(self) -> bool:
        """Sometimes for no reason TronGrid just returns 0 rows to a query that would otherwise return rows."""
        return self._was_successful() and self._page_size() == 0 and self.next_url() is None
