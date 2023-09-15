"""Base class for webpage"""
from __future__ import annotations

from abc import ABC

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag

from ..errors import ElementNotFoundError


class Webpage(ABC):
    """Base class for website"""

    url: str
    html: str
    soup: BeautifulSoup

    def __init__(self, load: bool = True) -> None:
        if load:
            self.load()

    def load(self):
        """Load webpage and set html and soup"""
        response = requests.get(self.url, timeout=10)
        response.raise_for_status()
        self.html = response.text
        self.soup = BeautifulSoup(self.html, "html.parser")

    def select_one(self, selector: str) -> Tag:
        """Select one element from soup"""
        res = self.soup.select_one(selector)
        if not res:
            raise ElementNotFoundError(f"{selector} not found in {self.url}")
        return res

    def select(self, selector: str) -> list[Tag]:
        """Select elements from soup"""
        res = self.soup.select(selector)
        if len(res) == 0:
            raise ElementNotFoundError(f"{selector} not found in {self.url}")
        return res
