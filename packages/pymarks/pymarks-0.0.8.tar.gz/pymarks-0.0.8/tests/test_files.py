from __future__ import annotations

import time
from datetime import datetime
from datetime import timezone
from pathlib import Path

import pytest

from pymarks.files import copy
from pymarks.files import delete
from pymarks.files import get_age_in_days
from pymarks.files import get_files
from pymarks.files import get_newest
from pymarks.files import get_oldest
from pymarks.files import latest_file_and_age


@pytest.fixture
def test_files(tmp_path):
    # Create temporary files for testing
    files = [
        tmp_path / 'file1.txt',
        tmp_path / 'file2.txt',
        tmp_path / 'file3.txt',
    ]
    for file in files:
        file.write_text('Test content')
        time.sleep(0.1)
    yield files
    # Cleanup the temporary files after testing
    for file in files:
        file.unlink()


def test_get_files(test_files):
    path = test_files[0].parent
    files = get_files(path, '*.txt')
    assert len(files) == 3
    assert all(isinstance(file, Path) for file in files)
    assert all(file.suffix == '.txt' for file in files)


def test_get_newest(test_files):
    newest_file = get_newest(test_files)
    assert newest_file == test_files[2]


def test_get_oldest(test_files):
    oldest_file = get_oldest(test_files)
    assert oldest_file == test_files[0]


def test_get_age_in_days(test_files):
    file = test_files[1]
    current_time = datetime.now(tz=timezone.utc).timestamp()
    file_timestamp = file.stat().st_mtime
    expected_age = (current_time - file_timestamp) / (24 * 60 * 60)
    age = get_age_in_days(file)
    assert age == pytest.approx(expected_age, abs=0.01)


def test_copy(tmp_path):
    source_file = tmp_path / 'source.txt'
    destination_file = tmp_path / 'destination.txt'
    source_file.write_text('Test content')
    copy(source_file, destination_file)
    assert destination_file.read_text() == 'Test content'


def test_delete(tmp_path):
    file_to_delete = tmp_path / 'file_to_delete.txt'
    file_to_delete.write_text('Test content')
    delete(file_to_delete)
    assert not file_to_delete.exists()


def test_latest_file_and_age(test_files):
    latest_file, age = latest_file_and_age(test_files)
    assert latest_file == test_files[2]
    assert age == pytest.approx(get_age_in_days(latest_file), abs=0.01)
