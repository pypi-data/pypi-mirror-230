"""Scraper for https://kabuyoho.jp/sp/reportTrendSignal"""
from __future__ import annotations

import logging
import re
import urllib.parse

from ..base import Website, webpage_property
from ..errors import ElementNotFoundError
from ..util import str2float
from .kabuyoho_webpage import KabuyohoWebpage

logger = logging.getLogger(__name__)


class ReportTrendSignal(KabuyohoWebpage):
    """Report target page object."""

    def __init__(self, website: Website, security_code: str | int) -> None:
        self.website = website
        self.security_code = str(security_code)
        self.url = urllib.parse.urljoin(self.website.url, f"sp/reportTrendSignal?bcode={self.security_code}")
        super().__init__()

    @webpage_property
    def trend_signal(self) -> str:
        """Trend signal: トレンドシグナル>今日のトレンドシグナル."""
        value = self.select_one('h2:-soup-contains("トレンドシグナル") + div > table > td')
        return value.text

    @webpage_property
    def coincident_index(self) -> float | None:
        """Coincident index: リスクオン相対指数>一致指数"""
        values = self.select('h2:-soup-contains("リスクオン相対指数") + div > table > tbody > td')
        if len(values) != 3:
            raise ElementNotFoundError("coincident_index")
        return str2float(values[0].text)

    @webpage_property
    def leading_index(self) -> float | None:
        """Leading index: リスクオン相対指数>先行指数"""
        values = self.select('h2:-soup-contains("リスクオン相対指数") + div > table > tbody > td')
        if len(values) != 3:
            raise ElementNotFoundError("leading_index")
        return str2float(values[1].text)

    @webpage_property
    def risk_on_relative_index_level(self) -> str | None:
        """Relative index: リスクオン相対指数>水準"""
        values = self.select('h2:-soup-contains("リスクオン相対指数") + div > table > tbody > td')
        if len(values) != 3:
            raise ElementNotFoundError("relative_index")
        value = re.sub(r"\s+", "", values[2].text)
        return value if value != "--" else None
