# Usage
## Command Line
The `extract_tron_events` script will extract events from Trongrid. Run `extract_tron_events --help` to see the command line options. `--since` and `--until` arguments should be specified in ISO8601 time format.

Examples:
```sh
# By address
extract_tron_events --until 2023-06-26T16:07:39+00:00 -t TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t

# For symbol (only works for some preconfigured tokens)
extract_tron_events --since 2023-06-26T16:07:39+00:00 -t USDT

# All events (not just 'Transfer')
extract_tron_events -t wstUSDT --e all

# Resume an extraction you already started
extract_tron_events --resume-csv events_HT_TDyvndWuvX5xTBwHPYJi7J3Yq8pq8yh62h.csv
```

## As Package
```python
from trongrid_extractoor.api import Api

Api().contract_events('TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t')
```
Arguments for `contract_events()` can be found [here](trongrid_extractoor/api.py).

`contract_events()` hits the `contracts/[CONTRACT_ADDRESS]/events` endpoint and can pull all transfers for a given contract by filtering for `event_name=Transfer`. Other endpoints like `contracts/[CONTRACT_ADDRESS]/transactions` don't seem to really work.

```python
contract_info = Api().get_contract('TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t')
```
`get_contract()` retrieves the ABI, deployer, etc. etc.


# Trongrid Documentation, Quirks, Etc.
**UPDATE: cirac July 2023 Trongrid appears to have fixed this issue and the `next` URL will actually give you more than 5 pages.**

When you make an API request to TronGrid they return you a page of results. If there are more than the page size (200 here) then the response includes a `next` key that has a URL you can hit to get the next page. Sounds convenient, right? Except it doesn't work. After 5 pages TronGrid will tell you your timespan is too big and please try again. This package is written to go around this "quirk" by backing up the `max_timestamp` parameter when it can't page any more.

* [Trongrid API documentation](https://developers.tron.network/v4.0/reference/note)


# Contributing
This project was developed with `poetry` and as such is probably easier to work with using `poetry` to manage dependencies in the dev environment. Install with:
```
poetry install --with=dev
```

## Running Tests
```
pytest
```

## Publishing to PyPi
### Configuration
1. `poetry config repositories.chain_argos_pypi https://upload.pypi.org/legacy/`
1. `poetry config pypi-token.chain_argos_pypi [API_TOKEN]`

### Publishing
1. Update `pyproject.toml` version number
1. Update `CHANGELOG.md`
1. `poetry publish --build --repository chain_argos_pypi`

## TODO
1. Walk forward not backward
1. Weird that this yielded dupes on the first page:
   ```
   {request_params.py:29} INFO - Request URL: https://api.trongrid.io/v1/contracts/TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t/events
   Params requesting 'Transfer' events from 2021-04-01T04:00:01+00:00 to 2021-04-01T05:00:00+00:00 (no extra params).
   {response.py:48} INFO - New query requesting data from 2021-04-01T04:00:01+00:00 to 2021-04-01T05:00:00+00:00.
   {progress_tracker.py:67} INFO -   Removed 11 duplicate transactions...
   ```
1. USDT looks incomplete here as 9pm was the last time:
   ```
   WARNING - 0 txns found. We seem to be stuck at 2020-07-09T21:04:24+00:00.
   [2023-06-29, 06:34:36 UTC] {logging_mixin.py:137} INFO -                     WARNING    Last request params:                   api.py:127
                             {'only_confirmed': 'true', 'limit': 200,
                             'min_timestamp': 1594252801000.0,
                             'max_timestamp': 1594328664000.0,
                             'event_name': 'Transfer'}
    ```
1. USDD around this time should be double checked:
   ```
    INFO       Returning 1000 transactions from _rescue_extraction(), modified params in place.                                    api.py:191
    INFO     Writing 1000 rows to 'events_USDD_written_2023-06-28T04.22.00.csv'...                                           csv_helper.py:17
    [06/28/23 10:22:34] INFO       Removed 200 duplicate transactions...                                                                   progress_tracker.py:47
    WARNING  0 txns found. We seem to be stuck at 2023-01-26T03:18:54+00:00.                                                       api.py:103
    WARNING    Last request params: {'only_confirmed': 'true', 'limit': 200, 'min_timestamp': 1483228800000.0, 'max_timestamp':    api.py:104
            1674703134000.0, 'event_name': 'Transfer'}
    ```
