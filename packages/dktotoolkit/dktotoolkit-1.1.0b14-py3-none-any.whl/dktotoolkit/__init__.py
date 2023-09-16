"""
toolkit library, for Discord Catho bot ("dkto")
"""

# Errors
from .exceptions import ParseError

# Variables
from .__version__ import (
    __author__,
    __author_email__,
    __copyright__,
    __description__,
    __license__,
    __title__,
    __version__,
    __pkg_name__,
)

# Functions
from .dict import dict2obj, invert_dict
from .list import replace_with_mask, castList
from .str import str2digit
from .datestr import parser_date, date2str
from .envvar import load_dotenv, getEnvironVar, getTimesReminder, task_watch_dotenv_file
from .exceptions import ParseError
from .functions import compatMode  # LEGACY
from .functions import compat_mode
from .function_recursive import recurs_function
from .parserhtml import ParserHTML
from .sqlite3 import recursive_sql
from .jsonlike import clean_json, replace_empty_strings_with_none
from .discordify import discordify, discordify_dict
from .aelf import call_api_aelf, get_aelf_office
from .verbose import write_message

# Declaration explicite de tous les modules (pep8)
__all__ = [
    'ParseError',
    '__author__', '__author_email__',
    '__copyright__', '__description__', '__license__',
    '__title__', '__version__', '__pkg_name__',
    'dict2obj', "invert_dict",
    'replace_with_mask', "castList",
    'str2digit',
    'parser_date', 'date2str',
    'load_dotenv', 'getEnvironVar', 'getTimesReminder','task_watch_dotenv_file',
    'write_message'
    'compat_mode',
    'compatMode',  # LEGACY
    'recurs_function',
    'ParserHTML',
    "recursive_sql",
    'clean_json', 'replace_empty_strings_with_none',
    'discordify', 'discordify_dict',
    "call_api_aelf", "get_aelf_office"
]
