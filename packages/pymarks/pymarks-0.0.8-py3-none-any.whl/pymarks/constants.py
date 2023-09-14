from __future__ import annotations

import os
import textwrap
from pathlib import Path
from typing import NewType

from pyselector import Menu

from pymarks.__about__ import __appname__
from pymarks.__about__ import __version__

ExitCode = NewType('ExitCode', int)
KeyCode = NewType('KeyCode', int)

# XDG
DEFAULT_USER_CONFIG = Path(
    os.environ.get('XDG_CONFIG_HOME', Path.home() / '.config')
)
DEFAULT_APP_HOME = DEFAULT_USER_CONFIG / __appname__.lower()
PYMARKS_HOME = Path(os.environ.get('PYMARKS_HOME', DEFAULT_APP_HOME)).resolve()

# Paths
DATABASES_DIR = PYMARKS_HOME / 'databases'
PYMARKS_BACKUP_DIR = PYMARKS_HOME / 'backup'

# Names
DB_DEFAULT_FILE = DATABASES_DIR / 'bookmarks.db'
DB_TRASH_FILE = DATABASES_DIR / 'trash.db'

# Backup
DEFAULT_BACKUP_MAX_AGE = 15
DEFAULT_BACKUP_MAX_AMOUNT = 3
PYMARKS_BACKUP_MAX_AGE = int(
    os.environ.get('PYMARKS_BACKUP_MAX_AGE', DEFAULT_BACKUP_MAX_AGE)
)
PYMARKS_BACKUP_MAX_AMOUNT = int(
    os.environ.get('PYMARKS_BACKUP_MAX_AMOUNT', DEFAULT_BACKUP_MAX_AMOUNT)
)

# Others
BULLET = '\u2022'
MENUS = list(Menu.registered().keys())

# App
APP_NAME = __appname__
APP_VERSION = __version__
APP_URL = 'https://github.com/haaag/PyMarks/'
APP_DESCRIPTION = textwrap.dedent(
    f"""
    {APP_NAME} is a simple tool to assist you in efficiently
    organizing and managing your bookmarks.

    The tool simplifies the process of accessing, adding, updating,
    and removing bookmarks.

    supported menus:
       {MENUS}
    """
)

APP_HELP = APP_DESCRIPTION
APP_HELP += textwrap.dedent(
    f"""
    options:
        -a, --add                   Add bookmark
        -m, --menu                  Select menu (default: rofi)
        -j, --json                  JSON formatted output
        -V, --version               Show version
        -h, --help                  Show help
        -v, --verbose               Verbose mode

    optional environment variables:
        PYMARKS_HOME                Overrides default {APP_NAME} location
        PYMARKS_BACKUP_MAX_AGE      Overrides backup age check interval
        PYMARKS_BACKUP_MAX_AMOUNT   Overrides backup max amount

    The default days for create backup is '{PYMARKS_BACKUP_MAX_AGE}' days.
    The default amount for keeping backups '{PYMARKS_BACKUP_MAX_AMOUNT}'
    The default app location is '{PYMARKS_HOME}'.
    """
)

# Bookmark
APP_BOOKMARK = (
    APP_URL,
    APP_NAME,
    'bookmarks,python,great',
    'Makes accessing, adding, updating, and removing bookmarks easier',
)
