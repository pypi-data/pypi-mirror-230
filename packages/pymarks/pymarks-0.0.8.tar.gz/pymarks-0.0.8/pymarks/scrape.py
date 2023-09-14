from __future__ import annotations

import logging
import re

import httpx
from bs4 import BeautifulSoup

log = logging.getLogger(__name__)


def page(url: str) -> BeautifulSoup:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',  # noqa: E501
        'Accept-Language': 'en-US',
        'Accept-Encoding': 'gzip, deflate',
        'Accept': 'text/html',
    }
    try:
        log.info(f'scraping {url}')
        page = httpx.get(url, timeout=10, headers=headers).text
        return BeautifulSoup(page, 'html5lib')
    except httpx.ReadTimeout:
        log.error(f'Timeout occurred while scraping {url}')
    except httpx.ConnectError:
        log.error(f'Connection error occurred while scraping {url}')


def title(soup: BeautifulSoup) -> str | None:
    title_tags = [
        ('title', {}),
        ('meta', {'name': 'title'}),
        ('meta', {'property': 'title'}),
        ('meta', {'name': 'og:title'}),
        ('meta', {'property': 'og:title'}),
    ]

    for tag, attrs in title_tags:
        title = soup.find(tag, attrs)
        if title:
            if tag == 'meta' and 'content' in title.attrs:
                return title.attrs['content'].strip()
            title_text = title.get_text().strip()
            if title_text:
                title_text = re.sub(r'\s{2,}', ' ', title_text)
                log.debug('title_text: %s', title_text)
                return title_text
    return None


def description(soup) -> str | None:
    description_tags = [
        ('meta', {'name': 'description'}),
        ('meta', {'name': 'Description'}),
        ('meta', {'property': 'description'}),
        ('meta', {'property': 'Description'}),
        ('meta', {'name': 'og:description'}),
        ('meta', {'name': 'og:Description'}),
        ('meta', {'property': 'og:description'}),
        ('meta', {'property': 'og:Description'}),
    ]

    for tag, attrs in description_tags:
        description = soup.find(tag, attrs)
        if description:
            desc = description.get('content').strip()
            if desc:
                desc = re.sub(r'\s{2,}', ' ', desc)
                log.debug('desc: %s', desc)
                return desc
    return None


def title_and_description(url: str) -> tuple[str | None, str | None]:
    soup = page(url)
    if not soup:
        return None, None
    return title(soup), description(soup)
