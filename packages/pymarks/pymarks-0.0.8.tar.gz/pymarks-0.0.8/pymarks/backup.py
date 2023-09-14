from __future__ import annotations

import logging
from datetime import datetime as dt
from datetime import timezone
from typing import TYPE_CHECKING

from pymarks import files

if TYPE_CHECKING:
    from pathlib import Path

log = logging.getLogger(__name__)


def create_backup(file: Path, backup_path: Path) -> None:
    """
    Create a backup of a file by copying it to a backup directory.

    Args:
        file (Path): The path to the file that needs to be backed up.
        backup_path (Path): The directory path where the backup will be stored.

    Returns:
        None
    """
    today = dt.now(tz=timezone.utc).strftime('%Y-%m-%d')
    name = f'{today}_{file.name}'
    backup_file = backup_path.joinpath(name)
    files.copy(file, backup_file)


def remove(backup: Path) -> None:
    log.info(f'Removing file: {backup}')
    files.delete(backup)


def clean_old_backups(backups: list[Path], max_backups: int) -> None:
    """
    Clean up old backups to retain the maximum number of backups specified.

    Args:
        backups (List[Path]): List of backup file paths.
        max_backups (int): Maximum number of backups to retain.

    Returns:
        None
    """
    if len(backups) == max_backups:
        return
    backups_to_delete, _ = get_backups_deprecated(
        backups,
        max_backups,
    )
    for backup_deprecated in backups_to_delete:
        remove(backup_deprecated)


def get_backups_deprecated(
    backups: list[Path], max_backups: int
) -> tuple[list[Path], list[Path]]:
    """
    Split the list of backup paths into backups to delete and backups to keep.
    """
    files_to_delete_len = len(backups) - max_backups
    backups_to_delete = backups[:files_to_delete_len]
    backups_to_keep = backups[files_to_delete_len:]
    return backups_to_delete, backups_to_keep


def get_backups(backup_path: Path) -> list[Path] | None:
    """
    Get a list of backup file paths sorted by modification time.

    Args:
        backup_path (Path): Path to the backup directory.

    Returns:
        Union[List[Path], None]: List of backup file paths sorted by modification time.
                                 Returns None if no backup files are found.
    """  # noqa: E501
    backups = files.get_files(backup_path, extension='*.db')
    if not backups:
        return None
    backups.sort(key=lambda path: path.stat().st_mtime)
    return backups


def check(
    database: Path, backup_path: Path, max_age: int, max_amount: int
) -> None:
    """
    Check backups in the specified backup path and perform necessary actions.

    Args:
        database_path (str): Path to the database.
        backup_path (str): Path to the backup directory.
        max_age_days (int): Maximum age of a backup in days before creating a new backup.
        max_amount (int): Maximum number of backups to retain.

    Returns:
        None
    """  # noqa: E501
    log.debug(f'Checking backups: {backup_path}')
    backups = get_backups(backup_path)

    if not backups:
        create_backup(database, backup_path)
        return
    newest_backup_age = files.get_newest(backups)
    if files.get_age_in_days(newest_backup_age) >= max_age:
        create_backup(database, backup_path)
        return
    if len(backups) > max_amount:
        clean_old_backups(backups, max_amount)
        return
    log.debug('Checking backups: nothing to do')
    return
