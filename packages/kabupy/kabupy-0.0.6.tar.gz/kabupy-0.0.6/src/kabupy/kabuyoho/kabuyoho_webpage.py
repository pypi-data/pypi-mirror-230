"""Base class for webpage"""
from __future__ import annotations

import re
from datetime import datetime

from money import Money

from ..base import Webpage, webpage_property
from ..util import str2money


class KabuyohoWebpage(Webpage):
    """Base class for kabuyoho webpage"""

    security_code: str

    def term2description(self, term: str) -> str:
        """Get dd text from dt text"""
        res = self.select_one(f'main dt:-soup-contains("{term}") + dd')
        return re.sub(r"\s+", "", res.text)

    @webpage_property
    def price(self) -> Money | None:
        """Price of the stock: 価格"""
        amount = self.select_one('main li p:-soup-contains("株価","(","/",")") + p')
        return str2money(amount.text)

    @webpage_property
    def name(self) -> str | None:
        """Name of the stock: 銘柄名"""
        res = self.select_one(f"main ul:-soup-contains('{self.security_code}') > li")
        return res.text

    @webpage_property
    def earnings_release_date(self) -> datetime | None:
        """Earnings release date: 決算発表日"""
        res = self.select_one(f"main ul:-soup-contains('{self.security_code}') > li:last-of-type")
        match = re.search(r"(\d{4})/(\d{2})/(\d{2})", res.text)
        if match:
            year, month, day = match.groups()
            return datetime(int(year), int(month), int(day))
        return None
