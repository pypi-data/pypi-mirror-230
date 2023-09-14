from __future__ import annotations

import logging
import sys
from typing import TYPE_CHECKING
from typing import Callable
from typing import Iterable

from pyselector import key_manager

from pymarks import constants
from pymarks import database
from pymarks import display
from pymarks import scrape
from pymarks import utils
from pymarks.bookmark import RecordForDB
from pymarks.constants import BULLET
from pymarks.constants import ExitCode
from pymarks.constants import KeyCode

if TYPE_CHECKING:
    from sqlite3 import Cursor

    from pyselector.selector import MenuInterface

    from pymarks.bookmark import Bookmark
    from pymarks.bookmark import PromptFn


log = logging.getLogger(__name__)


def show_bookmarks(
    cursor: Cursor,
    menu: MenuInterface,
    prompt: PromptFn,
    items: Iterable[Bookmark],
) -> Bookmark:
    bookmark_str, return_code = display.items(prompt=prompt, items=items)
    keycode = KeyCode(return_code)

    while keycode != ExitCode(0):
        try:
            keybind = menu.keybind.get_keybind_by_code(keycode)
            bookmark_str, keycode = keybind.callback(
                cursor,
                prompt,
                bookmark=bookmark_str,
                menu=menu,
                keybind=keybind,
            )
        except key_manager.KeybindError as err:
            log.warning(err)
            sys.exit(1)

    return database.get_bookmark_from_string(cursor, bookmark_str)


def create_bookmark(
    cursor: Cursor, prompt: PromptFn, **kwargs
) -> tuple[str, KeyCode] | None:
    kwargs['menu'].keybind.toggle_all()
    item = utils.read_from_clipboard()

    url, _ = prompt(
        prompt='New bookmark>',
        mesg='Reading <url> from clipboard',
        filter=item.strip(),
    )

    if database.exists_in_database(cursor, url):
        database_name = database.get_database_path(cursor).name
        mesg = f'> Bookmark already exists on database {database_name!r}'
        display.warning(prompt, mesg)
        return None

    tags, _ = prompt(
        prompt='Tags>',
        mesg=f'Add comma separated tags for <{url}>',
    )

    title, desc = scrape.title_and_description(url)
    record = RecordForDB(url=url, tags=tags, title=title, description=desc)
    bookmark = database.create_bookmark(cursor, record)

    return str(bookmark), KeyCode(0)


def delete_bookmark(cursor: Cursor, prompt: PromptFn, b: Bookmark) -> None:
    if not display.confirmation(msg=f'Deleting {b.url}?', prompt=prompt):
        return
    database.remove_bookmark(cursor, b)
    sys.exit(0)


def tag_selector(
    cursor: Cursor, prompt: PromptFn, **kwargs
) -> tuple[str, KeyCode]:
    kwargs['menu'].keybind.toggle_all()
    min_tag_len = 2
    tags = database.get_tags_count(cursor)
    tag_selected, _ = prompt(items=tags, mesg='Filter by tag')

    if len(tag_selected.split()) < min_tag_len:
        err_msg = f'Invalid tag: {tag_selected!r}'
        raise ValueError(err_msg)

    tag = tag_selected.split()[0]
    log.debug('Selected tag: %s', tag)
    records = database.get_bookmarks_by_tag(cursor, tag)
    bookmark, code = prompt(items=records, mesg=f'Filter by tag <{tag}>')
    return bookmark, KeyCode(code)


def options_selector(
    cursor: Cursor, prompt: PromptFn, **kwargs
) -> tuple[str, KeyCode]:
    kwargs['menu'].keybind.toggle_all()
    bookmark = database.get_bookmark_from_string(cursor, kwargs['bookmark'])

    options: dict[str, Callable] = {
        f'{BULLET} Edit': update_bookmark,
        f'{BULLET} Delete': delete_bookmark,
    }

    option_fn: Callable = display.options(
        options, prompt=prompt, mesg=f'{BULLET} Actions for <{bookmark.url}>'
    )

    option_fn(cursor, prompt, bookmark)

    return str(bookmark), KeyCode(0)


def update_bookmark(
    cursor: Cursor, prompt: PromptFn, b: Bookmark
) -> tuple[str, KeyCode]:
    options: dict[str, Callable] = {
        f'{BULLET} Title': update_title,
        f'{BULLET} Description': update_desc,
        f'{BULLET} Tags': update_tags,
        f'{BULLET} URL': update_url,
        f'{BULLET} Fetch Title/Desc': fetch_and_update,
    }
    option_fn: Callable = display.options(
        options, prompt, mesg=f'Options for <{b.url}>'
    )
    option_fn(cursor, prompt, b)
    return str(b), KeyCode(0)


def update_title(
    cursor: Cursor, prompt: PromptFn, b: Bookmark
) -> tuple[str, KeyCode]:
    title, _ = prompt(
        mesg=f'{BULLET} URL: {b.url}', prompt='New title >', filter=b.title
    )

    if not title:
        title = ''

    database.update_bookmark_title(cursor, b.id, title)
    return str(b), KeyCode(0)


def update_desc(
    cursor: Cursor, prompt: PromptFn, b: Bookmark
) -> tuple[str, KeyCode]:
    desc, _ = prompt(
        mesg=f'{BULLET} URL: {b.url}',
        prompt='New Desc >',
        filter=b.description,
    )

    if not desc:
        desc = ''

    database.update_bookmark_desc(cursor, b.id, desc)
    return str(b), KeyCode(0)


def update_tags(
    cursor: Cursor, prompt: PromptFn, b: Bookmark
) -> tuple[str, KeyCode]:
    tags, _ = prompt(
        mesg=f'{BULLET} URL: {b.url}', prompt='New Tags >', filter=b.tags
    )

    if not tags:
        tags = ','

    database.update_bookmark_tags(cursor, b.id, tags)
    return str(b), KeyCode(0)


def update_url(
    cursor: Cursor, prompt: PromptFn, b: Bookmark
) -> tuple[str, KeyCode]:
    url, _ = prompt(mesg=f'Updating URL: {b.url}', filter=b.url)
    database.update_bookmark_url(cursor, b.id, url)
    return str(b), KeyCode(0)


def fetch_and_update(
    cursor: Cursor, prompt: PromptFn, b: Bookmark
) -> tuple[str, KeyCode]:
    title, desc = scrape.title_and_description(b.url)
    confirmation = 'Accept changes?'

    items = [
        f'Title: {title}',
        f'Description: {desc}',
        confirmation,
    ]

    if not display.confirmation(
        msg=f'Update {b.url} with data fetched?',
        prompt=prompt,
        items=items,
        confirmation=confirmation,
    ):
        return str(b), KeyCode(0)

    b.title = title
    b.description = desc
    database.update_bookmark(cursor, b)
    return str(b), KeyCode(0)


def item_detail(
    cursor: Cursor, prompt: PromptFn, **kwargs
) -> tuple[str, KeyCode]:
    kwargs['menu'].keybind.toggle_all()
    bookmark = database.get_bookmark_from_string(cursor, kwargs['bookmark'])
    display.item_details(prompt, bookmark, icon=BULLET)
    return str(bookmark), KeyCode(0)


def database_selector(
    cursor: Cursor, prompt: PromptFn, **kwargs
) -> tuple[str, KeyCode]:
    kwargs['menu'].keybind.toggle_all()
    databases_path = list(constants.DATABASES_DIR.glob('*.db'))
    selected, _ = display.items(list(map(str, databases_path)), prompt=prompt)
    database_path = constants.DATABASES_DIR / selected

    if not database_path.exists():
        err_msg = f'Database not found: {database_path}'
        log.error(err_msg)
        raise FileNotFoundError(err_msg)

    with database.open_database(database_path) as cursor:
        records = database.get_bookmarks_all(cursor)
        bookmark_str, keycode = display.items(
            prompt=prompt, items=list(records)
        )

    return bookmark_str, KeyCode(0)
