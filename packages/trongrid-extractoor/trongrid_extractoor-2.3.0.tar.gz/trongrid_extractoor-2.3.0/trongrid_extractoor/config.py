import logging
from os import environ

from rich.logging import RichHandler
from trongrid_extractoor.helpers.string_constants import PACKAGE_NAME

LOG_LEVEL = environ.get('LOG_LEVEL', 'INFO')


log = logging.getLogger(PACKAGE_NAME)
