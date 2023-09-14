from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from pymarks import database
from pymarks import files
from pymarks.constants import APP_NAME
from pymarks.constants import BULLET
from pymarks.constants import DATABASES_DIR
from pymarks.constants import DEFAULT_APP_HOME
from pymarks.constants import DEFAULT_BACKUP_MAX_AGE
from pymarks.constants import DEFAULT_BACKUP_MAX_AMOUNT
from pymarks.constants import PYMARKS_BACKUP_DIR

if TYPE_CHECKING:
    from pathlib import Path
    from sqlite3 import Cursor

    from pyselector.interfaces import MenuInterface

    from pymarks.bookmark import PromptFn


"""
    > PROJECT:
        • Name:             :   PyMarks
        • Path              :   ~/.config/pymarks/
        • Databases path    :   ~/.config/pymarks/databases/
        • Backup path       :   ~/.config/pymarks/backup/
        • Backup interval   :   15 days
    > CURRENT DATABASE
        • Name              : bookmarks.db
        • Records           : 693
        • Last backup       : 2 day/s old
    > DATABASES (4)
        • Db-1              : bookmarks.db
        • Db-2              : private.db
        • Db-3              : trash.db
        • Db-4              : work.db
    > BACKUPS (3)
        • Bk-1              : 2023-06-23_bookmarks.db
        • Bk-2              : 2023-08-03_bookmarks.db
        • Bk-3              : 2023-08-18_bookmarks.db
    > Keybinds (6)
        • Alt-a             :   action=for add bookmark (return_code=10)
        • Alt-e             :   action=for options (return_code=11)
        • Alt-t             :   action=for filter by tag (return_code=12)
        • Alt-c             :   action=for change db (return_code=13)
        • Alt-d             :   action=for item detail (return_code=14)
        • Alt-i             :   action=for app information (return_code=15)
"""


def format_title(title: str, items: list[str]) -> list[str]:
    return [f'> {title}', *items]


def format_bullet_line(label: str, value: str) -> str:
    return f'    {BULLET} {label: <20}: {value}'


def get_project_information() -> list[str]:
    items = [
        format_bullet_line('Name', APP_NAME),
        format_bullet_line('Path', str(DEFAULT_APP_HOME)),
        format_bullet_line('Databases path', str(DATABASES_DIR)),
        format_bullet_line('Backup path', str(PYMARKS_BACKUP_DIR)),
        format_bullet_line('Backup interval', str(DEFAULT_BACKUP_MAX_AGE)),
        format_bullet_line('Backup max.', str(DEFAULT_BACKUP_MAX_AMOUNT)),
    ]
    return format_title('PROJECT', items)


def get_keybinds_information(menu: MenuInterface) -> list[str]:
    """
    > Keybinds (6)
        • Alt-a             :   action=for add bookmark (return_code=10)
        • Alt-e             :   action=for options (return_code=11)
        • Alt-t             :   action=for filter by tag (return_code=12)
        • Alt-c             :   action=for change db (return_code=13)
        • Alt-d             :   action=for item detail (return_code=14)
        • Alt-i             :   action=for app information (return_code=15)
    """
    items: list[str] = []
    for bind in menu.keybind.registered_keys:
        desc = f'action={bind.description}'
        return_code_str = f'(return_code={bind.code})'
        item = format_bullet_line(bind.bind, f'{desc: <40} {return_code_str}')
        items.append(item)
    title = f'> KEYBINDS ({len(menu.keybind.registered_keys)})'
    return format_title(title, items)


def old_get_keybinds_information(menu: MenuInterface) -> list[str]:
    """
    > Keybinds (6)
        • Alt-a             :   action=for add bookmark (return_code=10)
        • Alt-e             :   action=for options (return_code=11)
        • Alt-t             :   action=for filter by tag (return_code=12)
        • Alt-c             :   action=for change db (return_code=13)
        • Alt-d             :   action=for item detail (return_code=14)
        • Alt-i             :   action=for app information (return_code=15)
    """
    info: list[str] = []
    info.append(f'> KEYBINDS ({len(menu.keybind.registered_keys)})')
    for bind in menu.keybind.registered_keys:
        desc = f'action={bind.description}'
        return_code_str = f'(return_code={bind.code})'
        info.append(
            f'    {BULLET} {bind.bind: <20}: {desc: <40} {return_code_str}'
        )
    return info


def get_backup_age(backups: list[Path]) -> str:
    latest_backup, age = files.latest_file_and_age(backups)
    return 'today' if age == 0 else f'{age} day/s old'


def get_backups_information(backups: list[Path]) -> list[str]:
    """
    > BACKUPS (3)
        • Bk-0          : 2023-06-23_bookmarks.db
        • Bk-1          : 2023-08-03_bookmarks.db
        • Bk-2          : 2023-08-18_bookmarks.db
    """
    items: list[str] = []
    for idx, backup in enumerate(backups, start=1):
        items.append(format_bullet_line(f'Bk-{idx}', backup.name))
    return format_title(f'> BACKUPS ({len(backups)})', items)


def get_database_information(cursor: Cursor, backups: list[Path]) -> list[str]:
    db_name = database.get_database_path(cursor).name
    records = len(list(database.get_records_all(cursor)))
    last_backup = get_backup_age(backups)

    items: list[str] = []
    items.append(format_bullet_line('Name', db_name))
    items.append(format_bullet_line('Records', str(records)))
    items.append(format_bullet_line('Backup age', last_backup))
    return format_title('CURRENT DATABASE', items)


def get_databases_information() -> list[str]:
    databases = list(DATABASES_DIR.glob('*.db'))

    items: list[str] = []
    for idx, db in enumerate(databases, start=1):
        items.append(format_bullet_line(f'Db-{idx}', db.name))
    return format_title(f'DATABASES ({len(databases)})', items)


def get_app_information(
    cursor: Cursor, prompt: PromptFn, **kwargs
) -> list[str]:
    menu: MenuInterface = kwargs['menu']
    menu.keybind.toggle_all()
    backup_paths = list(PYMARKS_BACKUP_DIR.glob('*.db'))

    project = get_project_information()
    keybinds = get_keybinds_information(menu)
    current_db = get_database_information(cursor, backup_paths)
    databases = get_databases_information()
    backups = get_backups_information(backup_paths)

    all_details = project + current_db + databases + backups + keybinds
    prompt(items=all_details, mesg=f'{BULLET} App detail information')
    sys.exit(0)
