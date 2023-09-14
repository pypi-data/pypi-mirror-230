from __future__ import annotations

import logging

import httpx
import pytest
from bs4 import BeautifulSoup

from pymarks.scrape import description
from pymarks.scrape import page
from pymarks.scrape import title
from pymarks.scrape import title_and_description
from pymarks.scrape import validate


# Mocking the logger to avoid unnecessary log output during testing
class MockLogger(logging.Logger):
    def __init__(self, *args, **kwargs):
        self.handlers = []

    def addHandler(self, handler):
        pass

    def removeHandler(self, handler):
        pass

    def setLevel(self, level):
        pass

    def info(self, msg, *args, **kwargs):
        pass

    def error(self, msg, *args, **kwargs):
        pass

    def debug(self, msg, *args, **kwargs):
        pass


@pytest.fixture
def mock_logger(monkeypatch):
    # Replace the logger with the mock logger
    monkeypatch.setattr(logging, 'getLogger', MockLogger)


@pytest.fixture
def mock_httpx_get(monkeypatch):
    # Mocking the httpx.get() method to return a predefined HTML content
    def mock_get(url, timeout, headers):
        response = httpx.Response(
            200, content='<html><title>Test Title</title></html>'
        )
        return httpx.Response(
            request=httpx.Request('GET', url),
            status_code=200,
            content=response.content,
        )

    monkeypatch.setattr(httpx, 'get', mock_get)


@pytest.fixture
def sample_soup():
    # A sample BeautifulSoup object for testing
    return BeautifulSoup(
        "<html><title>Test Title</title><meta name='description' content='Test Description'></html>",
        'html5lib',
    )


def test_page(mock_logger, mock_httpx_get):
    soup = page('http://example.com')
    assert isinstance(soup, BeautifulSoup)
    assert soup.title.string == 'Test Title'


def test_title(sample_soup):
    title_text = title(sample_soup)
    assert title_text == 'Test Title'


def test_description(sample_soup):
    description_text = description(sample_soup)
    assert description_text == 'Test Description'


def test_title_and_description(mock_logger, mock_httpx_get):
    title_text, description_text = title_and_description('http://example.com')
    assert title_text == 'Test Title'
    assert description_text is None
