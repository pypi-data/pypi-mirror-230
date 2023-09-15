"""Scraper for https://kabuyoho.jp/sp/reportDps"""
from __future__ import annotations

import logging
import re
import urllib.parse
from datetime import datetime

from ..base import Website, webpage_property
from ..util import str2float, str2money
from .kabuyoho_webpage import KabuyohoWebpage

logger = logging.getLogger(__name__)


class ReportDps(KabuyohoWebpage):
    """Report target page object."""

    def __init__(self, website: Website, security_code: str | int) -> None:
        self.website = website
        self.security_code = str(security_code)
        self.url = urllib.parse.urljoin(self.website.url, f"sp/reportDps?bcode={self.security_code}")
        super().__init__()

    @webpage_property
    def dividend_history(self) -> list[dict]:
        """Dividend history(一株配当推移).

        Returns:
        list[dict]: List of dividend history.

        Note:
        The format of the list is as follows:
        [
        {"date": datetime(2021, 3, 1), "dividend": Money("55.0", "JPY")},
        {"date": datetime(2022, 3, 1), "dividend": Money("65.0", "JPY")},
        {"date": datetime(2023, 3, 1), "dividend": Money("75.0", "JPY")},
        {"date": datetime(2024, 3, 1), "dividend": None},
        ]
        """
        dates = self.select("h2:-soup-contains('一株配当推移') + div > table > tbody th")
        dates = [datetime.strptime(re.sub(r"[\D]", "", d.text), "%Y%m") for d in dates]
        dividends = self.select("h2:-soup-contains('一株配当推移') + div > table > tbody td")
        dividends = [str2money(d.text) for d in dividends]
        res = [{"date": date, "dividend": dividend} for date, dividend in zip(dates, dividends)]
        res.sort(key=lambda x: x["date"])
        return res

    @webpage_property
    def actual_dividend_yield(self) -> float | None:
        """Actual dividend yield(実績配当利回り)."""
        amount = self.select_one('th:-soup-contains("実績配当利回り") + td')
        return str2float(amount.text)

    @webpage_property
    def expected_dividend_yield(self) -> float | None:
        """Expected dividend yield(予想配当利回り)."""
        amount = self.select_one('th:-soup-contains("予想配当利回り") + td')
        return str2float(amount.text)

    @webpage_property
    def dividend_payout_ratio(self) -> float | None:
        """Dividend payout ratio(前期配当性向).

        Returns:
        float | None: Dividend payout ratio.
        """
        amount = self.select_one('h2:-soup-contains("前期配当性向") + div td')
        return str2float(amount.text)
