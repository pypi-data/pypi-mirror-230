from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

log = logging.getLogger(__name__)


def get_files(path: Path, extension: str) -> list[Path]:
    # TODO: Check if path is empty
    return list(path.glob(extension))


def get_newest(files: list[Path]) -> Path:
    return max(files, key=lambda file_path: file_path.stat().st_mtime)


def get_oldest(files: list[Path]) -> Path:
    return min(files, key=lambda item: item.stat().st_mtime)


def get_age_in_days(file_path: Path) -> float:
    file_stat = file_path.stat()
    creation_time = file_stat.st_mtime
    time_diff_seconds = time.time() - creation_time
    return round(time_diff_seconds / (24 * 60 * 60), 2)


def copy(source_file: Path, destination_file: Path) -> None:
    log.info(f'Creating copy: {destination_file!r}')
    destination_file.write_bytes(source_file.read_bytes())


def delete(file: Path) -> None:
    if not file.is_file():
        err_msg = f'{file=} not a file. Canceling...'
        return None
    if not file.exists():
        err_msg = f'{file=} not found. Canceling...'
        log.error(err_msg)
        raise ValueError(err_msg)
    return file.unlink()


def latest_file_and_age(files_path: list[Path]) -> tuple[Path, int]:
    latest_file = get_newest(files_path)
    age = get_age_in_days(latest_file)
    return latest_file, round(age)


def touch(file: Path) -> None:
    if not file.is_file():
        return
    log.info(f'Creating file: {file!r}')
    file.touch(exist_ok=True)


def mkdir(path: Path) -> None:
    if path.is_dir():
        return
    log.info(f'Creating directory: {path!r}')
    path.mkdir(parents=True, exist_ok=True)
