# from __future__ import annotations
#
# import logging
# import time
# from pathlib import Path
#
# import pytest
#
# from pymarks import backup
# from pymarks import constants
# from pymarks import files
#
# logging.basicConfig(level=logging.DEBUG)
# log = logging.getLogger(__name__)
#
#
# @pytest.fixture
# def test_files(tmp_path):
#     # create temporary files for testing
#     tmp_files = [
#         tmp_path / "file1.db",
#         tmp_path / "file2.db",
#         tmp_path / "file3.db",
#         tmp_path / "file4.db",
#     ]
#     for file in tmp_files:
#         file.write_text("test content")
#         # sleep for a short duration to ensure different file modification timestamps
#         time.sleep(0.1)
#     yield tmp_files
#     # cleanup the temporary files after testing
#     # for file in tmp_files:
#     #     file.unlink()
#
#
# def test_get_last_backup(test_files) -> None:
#     latest_backup = files.get_newest(test_files)
#     assert latest_backup == test_files[3]
#
#
# def test_get_backups(test_files) -> None:
#     backups = backup.get_backups(test_files[0].parent)
#     assert len(backups) == 4
#     assert backups[0] == test_files[0]
#
#
# def test_get_backups_deprecated(test_files) -> None:
#     to_delete, to_keep = backup.get_backups_deprecated(
#         test_files, constants.PYMARKS_BACKUP_MAX_AMOUNT
#     )
#     assert len(to_keep) <= constants.PYMARKS_BACKUP_MAX_AMOUNT
#     assert len(to_delete) == len(
#         test_files[constants.PYMARKS_BACKUP_MAX_AMOUNT :]
#     )
#
#
# def test_clean_backup(test_files) -> None:
#     backup_path = test_files[0].parent
#     backups = backup.clean_old_backups(
#         backup_path, constants.PYMARKS_BACKUP_MAX_AMOUNT
#     )
#     assert len(backups) == constants.PYMARKS_BACKUP_MAX_AMOUNT
#
#
# def test_check_last_backup_age_valid(test_files):
#     backup_dir = test_files[0].parent
#     create_backup = backup.has_old_backup(
#         backup_dir,
#         days=constants.DEFAULT_BACKUP_MAX_AGE,
#     )
#     assert create_backup is False
#
#
# def test_check_last_backup_age_invalid(test_files):
#     create_backup = backup.has_old_backup(
#         test_files[0].parent,
#         days=constants.DEFAULT_BACKUP_MAX_AGE,
#     )
#     assert create_backup is False
#
#
# def test_check_last_backup_age_empty_backup_list(tmp_path):
#     test_empty_directory = Path("/backup")
#     test_empty_directory.mkdir()
#
#     create_backup = backup.has_old_backup(
#         test_empty_directory,
#         days=constants.DEFAULT_BACKUP_MAX_AGE,
#         days=constants.DEFAULT_BACKUP_MAX_AGE,
#     )
