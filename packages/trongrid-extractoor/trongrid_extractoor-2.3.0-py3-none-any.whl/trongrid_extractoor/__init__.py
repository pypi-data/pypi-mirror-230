import logging
from os import environ
from sys import argv

from rich.logging import RichHandler
from rich.panel import Panel
from rich.pretty import pprint

from trongrid_extractoor.api import Api
from trongrid_extractoor.helpers.address_helpers import hex_to_tron, tron_to_hex
from trongrid_extractoor.helpers.argument_parser import parse_args
from trongrid_extractoor.helpers.string_constants import PACKAGE_NAME
from trongrid_extractoor.helpers.rich_helpers import console
from trongrid_extractoor.helpers.time_helpers import ms_to_datetime, datetime_to_ms


def extract_tron_events():
    """When called by the installed script use the Rich logger."""
    args = parse_args()

    Api().contract_events(
        args.contract_address,
        since=args.since,
        until=args.until,
        resume_from_csv=args.resume_from_csv,
        output_to=args.output_dir,
        event_name=args.event_name
    )


def epoch_ms_to_datetime():
    print(ms_to_datetime(int(argv[1])))


def datetime_to_epoch_ms():
    print(datetime_to_ms(argv[1]))


def hex_address_to_tron():
    print(hex_to_tron(argv[1]))


def tron_address_to_hex():
    print(tron_to_hex(argv[1]))


def tron_address_info():
    account = Api().get_account(argv[1])
    console.print(account)
    console.line()
    pprint(account.raw_dict_shortened(), expand_all=True)
    console.line()


def tron_contract_info():
    contract = Api().get_contract(argv[1], use_base58=True)
    console.line()
    console.print(contract)
    console.line()
    pprint(contract.raw_dict_shortened(), expand_all=True)
