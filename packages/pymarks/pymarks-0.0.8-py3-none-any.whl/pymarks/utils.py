# helpers.py

from __future__ import annotations

import logging
import shlex
import shutil
import subprocess
from typing import Any
from typing import NamedTuple

from pymarks import constants
from pymarks import database
from pymarks import files

log = logging.getLogger(__name__)


class BookmarkNotValidError(Exception):
    pass


class Clipboard(NamedTuple):
    copy: str
    paste: str


CLIPBOARDS: dict[str, Clipboard] = {
    'xclip': Clipboard(
        copy='xclip -selection clipboard',
        paste='xclip -selection clipboard -o',
    ),
    'xsel': Clipboard(
        copy='xsel -b -i',
        paste='xsel -b -o',
    ),
    'wl-copy': Clipboard(
        copy='wl-copy',
        paste='wl-paste',
    ),
}


def get_clipboard() -> Clipboard:
    for command, clipboard in CLIPBOARDS.items():
        if shutil.which(command):
            log.info(f'clipboard command: {clipboard!r}')
            return clipboard
    err_msg = 'No suitable clipboard command found.'
    log.error(err_msg)
    raise FileNotFoundError(err_msg)


def starts_with_digit(string: str) -> bool:
    if string and string[0].isdigit():
        return True
    return False


def extract_record_id(item: str) -> int:
    """Extracts the ID number from a string that represents a bookmark."""
    if not starts_with_digit(item):
        err_msg = f'not a valid bookmark id: {item!r}'
        log.error(err_msg)
        raise BookmarkNotValidError(err_msg)
    try:
        item_id = int(item.split()[0])
    except ValueError:
        err_msg = f'not a valid bookmark id: {item!r}'
        log.error(err_msg)
        raise BookmarkNotValidError(err_msg) from None
    return item_id


def parse_tags(tags: str) -> str:
    tags = ','.join([string.strip() for string in tags.split(',')])
    if tags.endswith(','):
        return tags
    return tags + ','


def stringify_dict(items: dict[str, Any]) -> list[str]:
    return [f'{k:<18}:\t{v:<30}' for k, v in items.items()]


def read_from_clipboard() -> str:
    """Read clipboard to add a new bookmark."""
    args = shlex.split(get_clipboard().paste)
    proc = subprocess.Popen(args, stdout=subprocess.PIPE)
    if proc.stdout is not None:
        data = proc.stdout.read()
        proc.stdout.close()
        return data.decode('utf-8')
    err_msg = 'Failed to start subprocess.'
    log.error(err_msg)
    raise RuntimeError(err_msg)


def copy_to_clipboard(item: str) -> int:
    """Copy selected item to the system clipboard."""
    data = item.encode('utf-8', errors='ignore')
    args = shlex.split(get_clipboard().copy)
    try:
        with subprocess.Popen(args, stdin=subprocess.PIPE) as proc:
            proc.stdin.write(data)  # type: ignore[union-attr]
            log.debug("Copied '%s' to clipboard", item)
    except subprocess.SubprocessError as e:
        log.error("Failed to copy '%s' to clipboard: %s", item, e)
        return 1
    return 0


def strtobool(val: str) -> bool:
    return val.lower() in ('true', 'on', '1')


def clean_string(s):
    for char in '<>#%^*()_+':
        s = s.replace(char, '')
    return s.replace('&', '&amp;')


def setup_project() -> None:
    files.mkdir(constants.PYMARKS_HOME)
    files.mkdir(constants.DATABASES_DIR)
    files.mkdir(constants.PYMARKS_BACKUP_DIR)
    files.touch(constants.DB_DEFAULT_FILE)
    database.init_database(constants.DB_DEFAULT_FILE)
    database.check_backup_files()
