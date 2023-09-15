"""Scraper for https://kabuyoho.jp/sp/reportDps"""
from __future__ import annotations

import functools
import logging
import re
import time
import urllib.parse
from datetime import datetime

from ..base import Website
from ..constants import TIME_SLEEP
from ..errors import ElementNotFoundError
from .kabuyoho_webpage import KabuyohoWebpage

logger = logging.getLogger(__name__)


class ReportNews(KabuyohoWebpage):
    """Report news page object."""

    def __init__(self, website: Website, security_code: str | int) -> None:
        self.website = website
        self.security_code = str(security_code)
        self.url = urllib.parse.urljoin(self.website.url, f"sp/reportNews?bcode={self.security_code}")
        # No need to call super().__init__() because this class does not have any webpage property.
        super().__init__(load=False)

    @functools.cached_property
    def market_report(self) -> KabuyohoNewsWebpage:
        """Market report page in a report news page."""
        return KabuyohoNewsWebpage(self.website, self.security_code, 1)

    @functools.cached_property
    def flash_report(self) -> KabuyohoNewsWebpage:
        """Flash report page in a report news page."""
        return KabuyohoNewsWebpage(self.website, self.security_code, 2)

    @functools.cached_property
    def analyst_prediction(self) -> KabuyohoNewsWebpage:
        """Analyst prediction page in a report news page."""
        return KabuyohoNewsWebpage(self.website, self.security_code, 3)

    @functools.cached_property
    def analyst_evaluation(self) -> KabuyohoNewsWebpage:
        """Analyst evaluation page in a report news page."""
        return KabuyohoNewsWebpage(self.website, self.security_code, 4)


class KabuyohoNewsWebpage(KabuyohoWebpage):
    """Kabuyoho news page object."""

    def __init__(self, website: Website, security_code: str | int, category: int) -> None:
        self.website = website
        self.security_code = str(security_code)
        self.category = category
        self.url = urllib.parse.urljoin(
            self.website.url, f"sp/reportNews?bcode={self.security_code}&cat={self.category}"
        )
        super().__init__()

    def get_max_page(self) -> int:
        """Max page number."""
        try:
            page = self.select_one("div.pager > ul > li.interval + li")
        except ElementNotFoundError:
            return 1
        return int(re.sub(r"[\D]", "", page.text))

    # ニュースがないかあるか判定する関数
    def has_links(self) -> bool:
        """True if there are news."""
        try:
            if self.select_one('div.sp_news_list li:-soup-contains("該当するニュースがございません。")'):
                return False
        except ElementNotFoundError:
            pass
        return True

    def get_links(self, max_page: int | None = 1, time_sleep: float = TIME_SLEEP) -> list[dict]:
        """list of links.

        Args:
            max_page (int | None, optional): Max page number. Defaults to 1. If None, all pages are scraped.

        Returns:
            list[dict]: List of news.

        Note:
            The example of the return value is as follows:
            [
                {
                    "date": datetime(2021, 3, 1, 12, 34),
                    "title": "FooBar",
                    "category": "決算",
                    "weather": "wthr_clud",
                    "url": "https://kabuyoho.jp/sp/example"
                },
                ...
            ]
        """
        res = []
        if not self.has_links():
            return res
        if max_page is None:
            max_page = self.get_max_page()
        else:
            max_page = min(max_page, self.get_max_page())
        for _page in range(1, max_page + 1):
            if _page > 1:
                time.sleep(time_sleep)
                self.url = self.url + f"&page={_page}"
                self.load()
            dates = self.select("div.sp_news_list > ul span.time")
            dates = [datetime.strptime(re.sub(r"[\D]", "", d.text), "%Y%m%d%H%M") for d in dates]
            titles = self.select("div.sp_news_list > ul p.list_title")
            titles = [t.text for t in titles]
            categories = self.select("div.sp_news_list > ul span.ctgr")
            categories = [c.text for c in categories]
            weathers = self.select("div.sp_news_list > ul span.wthr")
            weathers = [w.get_attribute_list("class") for w in weathers]
            weathers = [[w for w in weather if w != "wthr"] for weather in weathers]
            weathers = [weather[0] if len(weather) > 0 else None for weather in weathers]
            urls = self.select("div.sp_news_list > ul a")
            urls = [u.get("href") for u in urls]
            urls = [urllib.parse.urljoin(self.website.url, u) for u in urls if isinstance(u, str)]
            res = res + [
                {"date": date, "title": title, "category": category, "weather": weather, "url": url}
                for date, title, category, weather, url in zip(dates, titles, categories, weathers, urls)
            ]
        return res
