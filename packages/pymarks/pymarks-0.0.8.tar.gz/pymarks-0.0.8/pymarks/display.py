from __future__ import annotations

import logging
import typing
from typing import Callable
from typing import Iterable

from pymarks import utils

if typing.TYPE_CHECKING:
    from pymarks.bookmark import Bookmark
    from pymarks.bookmark import PromptFn


log = logging.getLogger(__name__)


def records(prompt: PromptFn, records: list[str]) -> int:
    item, code = prompt(prompt=f'{len(records)} Records>', items=records)
    return utils.extract_record_id(item)


def items(
    items: Iterable[Bookmark] | list[str],
    prompt: PromptFn,
) -> tuple[str, int]:
    item, code = prompt(items=items)
    return item, code


def warning(prompt: PromptFn, msg: str) -> None:
    prompt([msg])


def confirmation(
    prompt: PromptFn,
    msg: str,
    prompt_msg: str = 'Confirm>',
    items: list[str] | None = None,
    confirmation: str = 'Yes',
) -> bool:
    if not items:
        items = ['Yes', 'No']

    item, _ = prompt(
        case_sensitive=True,
        prompt=prompt_msg,
        items=items,
        mesg=msg,
    )
    log.debug('Confirmation: %s', item)
    return item == confirmation


def item(prompt: PromptFn, info: list[str], mesg: str) -> str:
    item, _ = prompt(items=info, mesg=mesg)
    return item


def options(
    option: dict[str, Callable], prompt: PromptFn, mesg: str
) -> Callable:
    item, _ = prompt(items=list(option.keys()), mesg=mesg)
    return option[item]


def item_details(prompt: PromptFn, b: Bookmark, icon: str) -> str:
    mesg = f'Details for <{b.url}>'
    info = [
        f'{icon} ID: {b.id}',
        f'{icon} Title: {b.title}',
        f'{icon} URL: {b.url}',
        f'{icon} Description: {b.description}',
        f'{icon} Tags: {b.tags}',
    ]
    item, _ = prompt(items=info, mesg=mesg)
    return item
