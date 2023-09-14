# datatypes.py

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

PromptFn = Callable[..., tuple[str, int]]
DatabaseRecord = tuple[int, str, str, str, str]


@dataclass
class RecordForDB:
    url: str
    tags: str
    title: str | None
    description: str | None


@dataclass
class Bookmark:
    id: int  # noqa: A003
    url: str
    title: str | None
    tags: str
    description: str | None

    def __str__(self) -> str:
        max_url_length = 80
        url = self.url[:max_url_length]
        tags = self.tags[:max_url_length]

        id_str = str(self.id).ljust(5)
        url_str = url.ljust(max_url_length)
        tags_str = tags.ljust(max_url_length)
        return f'{id_str} {url_str} {tags_str}'
