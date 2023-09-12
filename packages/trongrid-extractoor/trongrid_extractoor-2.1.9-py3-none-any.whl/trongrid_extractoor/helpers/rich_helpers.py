"""
Helpers for colored output with the Rich package.
"""
from sys import exit

from rich.console import Console
from rich.text import Text

console = Console(color_system='256')


def print_error_and_exit(error_msg: str) -> None:
    txt = Text('').append('ERROR', style='bright_red').append(f": {error_msg}")
    console.print(txt)
    exit(1)
