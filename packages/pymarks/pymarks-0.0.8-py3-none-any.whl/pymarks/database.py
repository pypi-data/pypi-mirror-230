# database.py

from __future__ import annotations

import json
import logging
import sqlite3
import sys
from collections import Counter
from contextlib import contextmanager
from datetime import datetime as dt
from datetime import timezone
from pathlib import Path
from sqlite3 import Cursor
from typing import Generator
from typing import Iterable

from pymarks import constants
from pymarks import utils
from pymarks.bookmark import Bookmark
from pymarks.bookmark import DatabaseRecord
from pymarks.bookmark import RecordForDB

log = logging.getLogger(__name__)


def parse_record_from_db(b: DatabaseRecord) -> Bookmark:
    return Bookmark(id=b[0], url=b[1], title=b[2], tags=b[3], description=b[4])


@contextmanager
def open_database(filepath: Path) -> Generator[sqlite3.Cursor, None, None]:
    connection = sqlite3.connect(
        filepath, detect_types=sqlite3.PARSE_DECLTYPES
    )
    try:
        cursor = connection.cursor()
        log.info('connected to %s', filepath)
        yield cursor
    except sqlite3.Error as e:
        log.error(e)
    finally:
        connection.commit()
        connection.close()


def init_database(database_path: Path) -> None:
    with open_database(database_path) as cursor:
        log.debug(f'Creating database={database_path!r}')
        schema = """
            CREATE TABLE IF NOT EXISTS bookmarks (
                id INTEGER PRIMARY KEY,
                url TEXT NOT NULL UNIQUE,
                title TEXT DEFAULT "",
                tags TEXT DEFAULT ",",
                desc TEXT DEFAULT "",
                created_at TIMESTAMP,
                last_used TIMESTAMP
            )
        """
        cursor.execute(schema)


def insert_initial_record(cursor: Cursor) -> None:
    bookmark = RecordForDB(*constants.APP_BOOKMARK)
    create_bookmark(cursor, bookmark)


def get_records_all(cursor: Cursor) -> sqlite3.Cursor:
    return cursor.execute('SELECT * from bookmarks ORDER BY id;')


def get_bookmark_by_id(cursor: Cursor, bid: int) -> Bookmark:
    cursor.execute('SELECT * from bookmarks WHERE id=:id', {'id': bid})
    bookmark = cursor.fetchone()
    if not bookmark:
        err_msg = f'No bookmarks found with id={bid}'
        log.error(err_msg)
        raise ValueError(err_msg)
    return parse_record_from_db(bookmark)


def get_bookmark_by_url(cursor: Cursor, url: str) -> Bookmark:
    query = 'SELECT * from bookmarks WHERE url=:url'
    cursor.execute(query, {'url': url})
    bookmark = cursor.fetchone()
    if not bookmark:
        err_msg = f'No bookmark found with url={url}'
        log.error(err_msg)
        raise ValueError(err_msg)
    return parse_record_from_db(bookmark)


def get_bookmarks_by_tag(cursor: Cursor, tag: str) -> Iterable[Bookmark]:
    cursor.execute(
        'SELECT * from bookmarks WHERE tags LIKE ?', ('%' + tag + '%',)
    )
    return (parse_record_from_db(record) for record in cursor.fetchall())


def get_bookmarks_by_query(
    cursor: Cursor, search: list[str]
) -> Iterable[Bookmark]:
    names = '%'.join(search)
    query = """
        SELECT * FROM bookmarks
        WHERE title LIKE ? OR url LIKE ? or tags LIKE ? or desc LIKE ?
    """
    pattern = f'%{names}%'
    bindings = (pattern, pattern, pattern, pattern)
    return (
        parse_record_from_db(record)
        for record in cursor.execute(query, bindings)
    )


def get_bookmarks_by_frequency(cursor: Cursor) -> Iterable[Bookmark]:
    cursor.execute('SELECT * from bookmarks ORDER BY frequency DESC;')
    return (parse_record_from_db(record) for record in cursor.fetchall())


def get_bookmarks_by_recent_use(cursor: Cursor) -> Iterable[Bookmark]:
    cursor.execute('SELECT * from bookmarks ORDER BY last_used DESC;')
    return (parse_record_from_db(record) for record in cursor.fetchall())


def get_bookmarks_without_title(cursor: Cursor) -> Iterable[Bookmark]:
    cursor.execute('SELECT * from bookmarks WHERE title IS NULL;')
    return (parse_record_from_db(record) for record in cursor.fetchall())


def get_bookmarks_without_desc(cursor: Cursor) -> Iterable[Bookmark]:
    cursor.execute('SELECT * from bookmarks WHERE desc IS NULL;')
    return (parse_record_from_db(record) for record in cursor.fetchall())


def get_bookmark_from_string(cursor: Cursor, record: str) -> Bookmark:
    record_id = utils.extract_record_id(record)
    return get_bookmark_by_id(cursor, record_id)


def get_bookmarks_all(cursor: Cursor) -> Iterable[Bookmark]:
    return (parse_record_from_db(b) for b in get_records_all(cursor))


def get_unique_tags(cursor: Cursor) -> list[str]:
    unique_tags = set()
    for b in get_bookmarks_all(cursor):
        unique_tags.update(b.tags.split(','))
    return sorted(unique_tags)


def get_tags_count(cursor: Cursor) -> list[str]:
    tags = [
        tag.strip()
        for b in get_bookmarks_all(cursor)
        for tag in b.tags.split(',')
        if tag.strip()
    ]
    counter = Counter(tags)
    sorted_results = sorted(counter.items())
    return [f'{element} ({count})' for element, count in sorted_results]


def update_bookmark(cursor: Cursor, b: Bookmark) -> None:
    query = 'UPDATE bookmarks SET url=?, title=?, tags=?, desc=? WHERE id=?'
    tags = utils.parse_tags(b.tags)
    cursor.execute(query, (b.url, b.title, tags, b.description, b.id))
    log.debug('Updating bookmark with id=%s', b.id)


def update_bookmark_title(cursor: Cursor, bid: int, title: str) -> None:
    query = 'UPDATE bookmarks SET title = ? WHERE id = ?'
    cursor.execute(query, (title, bid))
    log.debug('Bookmark with id=%s updated title=%s', bid, title)


def update_bookmark_desc(cursor: Cursor, bid: int, desc: str) -> None:
    query = 'UPDATE bookmarks SET desc = ? WHERE id = ?'
    cursor.execute(query, (desc, bid))
    log.debug('Bookmark with id=%s updated desc=%s', bid, desc)


def update_bookmark_tags(cursor: Cursor, bid: int, tags: str) -> None:
    tags = utils.parse_tags(tags)
    query = 'UPDATE bookmarks SET tags = ? WHERE id = ?'
    cursor.execute(query, (tags, bid))
    log.debug('Bookmark with id=%s updated tags=%s', bid, tags)


def update_bookmark_url(cursor: Cursor, bid: int, url: str) -> None:
    query = 'UPDATE bookmarks SET url = ? WHERE id = ?'
    cursor.execute(query, (url, bid))
    log.debug('Bookmark with id=%s updated url=%s', bid, url)


def update_bookmark_last_use(cursor: Cursor, bid: int) -> None:
    query = 'UPDATE bookmarks SET last_used = ? WHERE id = ?'
    cursor.execute(query, (dt.now(tz=timezone.utc), bid))


def update_bookmark_frequency_use(cursor: Cursor, bid: int) -> None:
    query = 'UPDATE bookmarks SET frequency = frequency + 1 WHERE ID = ?'
    cursor.execute(query, (bid,))


def reset_frequency_by_id(cursor: Cursor, bid: int) -> None:
    query = 'UPDATE bookmarks SET frequency = 0 WHERE id = ?'
    cursor.execute(query, (bid,))


def exists_in_database(cursor: Cursor, url: str) -> bool:
    log.debug(f"Checking if record '{url}' already exists")
    query = 'SELECT COUNT(*) FROM bookmarks WHERE url=?'
    cursor.execute(query, (url,))
    result = cursor.fetchone()[0]
    return result > 0


def create_bookmark(cursor: Cursor, b: RecordForDB | Bookmark) -> Bookmark:
    query = """
        INSERT INTO bookmarks(
            url,
            title,
            tags,
            desc,
            created_at) VALUES (?, ?, ?, ?, ?)"""
    tags = utils.parse_tags(b.tags)
    cursor.execute(
        query, (b.url, b.title, tags, b.description, dt.now(tz=timezone.utc))
    )
    last_row_id = cursor.lastrowid

    if last_row_id is None:
        err_msg = 'last row id is None'
        log.error(err_msg)
        raise ValueError(err_msg)

    bookmark = get_bookmark_by_id(cursor, last_row_id)
    db_name = get_database_path(cursor).name
    info_msg = f'New record with id={bookmark.id!r} url={bookmark.url!r}'
    info_msg += f' on database={db_name!r}'
    log.info(info_msg)
    return bookmark


def remove_bookmark(cursor: Cursor, b: Bookmark) -> None:
    query = 'DELETE from bookmarks WHERE id=?'
    cursor.execute(query, (b.id,))
    log.info('Removing record with id=%s and  url=%s', b.id, b.url)
    save_to_database(constants.DB_TRASH_FILE, b)


def save_to_database(database_path: Path, b: Bookmark) -> None:
    with open_database(database_path) as cursor:
        log.debug(f'Saving bookmark to {database_path.name}')
        init_database(database_path)
        create_bookmark(cursor, b)


def dump_to_json(records: Iterable[Bookmark]) -> None:
    from signal import SIG_DFL
    from signal import SIGPIPE
    from signal import signal

    signal(SIGPIPE, SIG_DFL)
    items = [item.__dict__ for item in records]
    print(json.dumps(items, sort_keys=True, indent=4))  # noqa: T201


def reset_all_frequency(cursor: Cursor) -> None:
    query = 'UPDATE bookmarks SET frequency = 0;'
    confirm = input("Resetting 'frequency' column, are you sure? [y/N]: ")
    if confirm.lower() not in ['yes', 'y']:
        sys.exit(1)
    cursor.execute(query)


def get_database_path(cursor: Cursor) -> Path:
    cursor.execute('PRAGMA database_list')
    database_info = cursor.fetchall()
    database_path = database_info[0][2]
    return Path(database_path)


def check_backup_files() -> None:
    from pymarks import backup

    if constants.PYMARKS_BACKUP_MAX_AGE == 0:
        return
    backup.check(
        database=constants.DB_DEFAULT_FILE,
        backup_path=constants.PYMARKS_BACKUP_DIR,
        max_age=constants.PYMARKS_BACKUP_MAX_AGE,
        max_amount=constants.PYMARKS_BACKUP_MAX_AMOUNT,
    )
