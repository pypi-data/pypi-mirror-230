"""Scraper for jpx.co.jp"""
from __future__ import annotations

import functools
import urllib.parse

import pandas as pd
import requests
from bs4 import BeautifulSoup

from ..base import Website
from ..exceptions import KabupyError


class Jpx(Website):
    """An object for jpx.co.jp"""

    def __init__(self) -> None:
        self.url = "https://www.jpx.co.jp"

    @functools.cached_property
    def issues_link(self) -> str:
        """Return a link to the issues list."""
        response = requests.get("https://www.jpx.co.jp/markets/statistics-equities/misc/01.html", timeout=10)
        response.raise_for_status()
        response.encoding = response.apparent_encoding
        soup = BeautifulSoup(response.text, "html.parser")
        href = soup.select_one('th:-soup-contains("東証上場銘柄一覧") + td>a')
        if href is None:
            raise KabupyError("no link was found.")
        href = href.attrs["href"]
        return urllib.parse.urljoin(self.url, href)

    @functools.cached_property
    def issues(self):
        """Return a list of issues."""
        link = self.issues_link
        response = requests.get(link, timeout=10)
        response.raise_for_status()
        return pd.read_excel(
            response.content,
            names=[
                "date",
                "security_code",
                "name",
                "category",
                "33_industry_code",
                "33_industry_category",
                "17_industry_code",
                "17_industry_category",
                "market_capitalization_code",
                "market_capitalization_category",
            ],
        ).to_dict("records")
