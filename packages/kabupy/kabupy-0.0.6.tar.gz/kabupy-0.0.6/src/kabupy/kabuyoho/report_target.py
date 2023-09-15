"""Scraper for https://kabuyoho.jp/sp/reportTop"""
from __future__ import annotations

import logging
import re
import urllib.parse

from money import Money

from ..base import Website, webpage_property
from ..util import str2float, str2int, str2money
from .kabuyoho_webpage import KabuyohoWebpage

logger = logging.getLogger(__name__)


class ReportTarget(KabuyohoWebpage):
    """Report target page object."""

    def __init__(self, website: Website, security_code: str | int) -> None:
        self.website = website
        self.security_code = str(security_code)
        self.url = urllib.parse.urljoin(self.website.url, f"sp/reportTarget?bcode={self.security_code}")
        super().__init__()

    # Properties in "price target(目標株価)"

    @webpage_property
    def price_level_to_target(self) -> str | None:
        """Current price level to target price: 目標株価に対する現在の価格が割高か割安か."""
        return None if self.term2description("目標株価から見た株価") == "--" else self.term2description("目標株価から見た株価")

    @webpage_property
    def price_target(self) -> Money | None:
        """Price target: 目標株価(アナリストが発表した目標株価の平均値)"""
        amount = self.select_one('thead:has(>tr>th:-soup-contains("平均")) ~ tbody>tr>td:nth-of-type(1)')
        return str2money(amount.text)

    @webpage_property
    def price_target_ratio_to_previous_week(self) -> float | None:
        """Price target ratio to previous week in %: 目標株価の対前週変化率"""
        amount = self.select_one('thead:has(>tr>th:-soup-contains("平均")) ~ tbody>tr>td:nth-of-type(2)')
        return str2float(amount.text)

    @webpage_property
    def price_target_ratio_to_current_price(self) -> float | None:
        """(price target) / (current price) in %: 目標株価と現在の株価の乖離率"""
        amount = self.select_one('thead:has(>tr>th:-soup-contains("平均")) ~ tbody>tr>td:nth-of-type(3)')
        return str2float(amount.text)

    # Properties in "rating(レーティング)"

    @webpage_property
    def average_analyst_rating(self) -> float | None:
        """Average analyst rating: レーティング(平均)"""
        amount = self.select_one('main section:has(h1:-soup-contains("レーティング")) th:-soup-contains("平均") + td')
        return str2float(amount.text)

    @webpage_property
    def analyst_count(self) -> int | None:
        """Average count: レーティング(人数)"""
        amount = self.select_one('main section:has(h1:-soup-contains("レーティング")) th:-soup-contains("人数") + td')
        amount = re.sub(r"\D", "", amount.text)
        if amount == "":
            amount = "0"
        return int(amount, 10)

    @webpage_property
    def analyst_rating_composition(self) -> dict[str, int]:
        """Analyst rating composition: レーティング(点数の構成)

        Returns:
            dict[str, int]: key: rating("1", "2", "3", "4", and "5"),
                            which respectively means
                            "strong sell(弱気)", "sell(やや弱気)", "hold(中立)", "buy(やや強気)", and "strong buy(強気)"
                            value: the number of analysts
        """
        ratings = ["1", "2", "3", "4", "5"]
        composition = {}
        for rating in ratings:
            res = self.select_one(
                'main h1:-soup-contains("レーティング") + div ' f'tbody tr>th:-soup-contains("({rating}点)") + td'
            )
            composition[rating] = str2int(res.text)
        return composition

    # Properties in "stock index(株価指標)"

    @webpage_property
    def bps(self) -> Money | None:
        """Book-value per share: BPS(実績)"""
        amount = self.select_one('main h2:-soup-contains("株価指標") + table th:-soup-contains("BPS(実績)") + td')
        return str2money(amount.text)

    @webpage_property
    def forward_eps(self) -> Money | None:
        """Forward earnings per share: EPS(予想)"""
        amount = self.select_one('main h2:-soup-contains("株価指標")+table th:-soup-contains("EPS(予想)") + td')
        return str2money(amount.text)

    @webpage_property
    def forward_eps_by_analysts(self) -> Money | None:
        """Forward earnings per share in twelve months based on analysts estimates: EPS(アナリスト12ヶ月後予想)"""
        amount = self.select_one('main h2:-soup-contains("株価指標")+table th:-soup-contains("EPS ※") + td')
        return str2money(amount.text)

    @webpage_property
    def pbr(self) -> float | None:
        """Price to book ratio: PBR"""
        amount = self.select_one('main h2:-soup-contains("株価指標")+table th:-soup-contains("PBR") + td')
        return str2float(amount.text)

    @webpage_property
    def forward_per(self) -> float | None:
        """Forward price to earnings ratio based on company estimates: PER(会予)"""
        amount = self.select_one('main h2:-soup-contains("株価指標")+table th:-soup-contains("PER(会予)") + td')
        return str2float(amount.text)

    @webpage_property
    def forward_per_by_analysts(self) -> float | None:
        """Forward PER in twelve months based on analysts estimates: PER(アナリスト12ヶ月後予想)"""
        amount = self.select_one('main h2:-soup-contains("株価指標")+table th:-soup-contains("PER ※") + td')
        return str2float(amount.text)

    # Properties in "target price range(想定株価レンジ)"

    @webpage_property
    def pbr_based_fair_value(self) -> Money | None:
        """PBR based fair value: 理論株価(PBR基準)"""
        value = self.select_one(
            'main h2:-soup-contains("想定株価レンジ") + '
            'table tr>th:-soup-contains("理論株価(PBR基準)") + '
            "td>span:nth-of-type(1)"
        )
        return str2money(value.text)

    @webpage_property
    def pbr_fair(self) -> float | None:
        """PBR when the stock price is at pbr_based_fair_value: 理論株価(PBR基準)の時のPBR"""
        value = self.select_one(
            'main h2:-soup-contains("想定株価レンジ") + '
            'table tr>th:-soup-contains("理論株価(PBR基準)") + '
            "td>span:nth-of-type(2)"
        )
        return str2float(value.text)

    @webpage_property
    def pbr_based_ceiling(self) -> Money | None:
        """PBR based ceiling price of the stock: 上値目途(PBR基準)"""
        value = self.select_one(
            'main h2:-soup-contains("想定株価レンジ") + '
            'table tr:has(>th:-soup-contains("理論株価(PBR基準)")) ~ '
            'tr>th:-soup-contains("上値目途") + td>span:nth-of-type(1)'
        )
        return str2money(value.text)

    @webpage_property
    def pbr_ceiling(self) -> float | None:
        """PBR when the stock price is at pbr_based_ceiling: 下値目途(PBR基準)の時のPBR"""
        value = self.select_one(
            'main h2:-soup-contains("想定株価レンジ") + '
            'table tr:has(>th:-soup-contains("理論株価(PBR基準)")) ~ '
            'tr>th:-soup-contains("上値目途") + td>span:nth-of-type(2)'
        )
        return str2float(value.text)

    @webpage_property
    def pbr_based_floor(self) -> Money | None:
        """PBR based floor price of the stock: 下値目途(PBR基準)"""
        value = self.select_one(
            'main h2:-soup-contains("想定株価レンジ") + '
            'table tr:has(>th:-soup-contains("理論株価(PBR基準)")) ~ '
            'tr>th:-soup-contains("下値目途") + td>span:nth-of-type(1)'
        )
        return str2money(value.text)

    @webpage_property
    def pbr_floor(self) -> float | None:
        """PBR when the stock price is at pbr_based_floor: 下値目途(PBR基準)の時のPBR"""
        value = self.select_one(
            'main h2:-soup-contains("想定株価レンジ") + '
            'table tr:has(>th:-soup-contains("理論株価(PBR基準)")) ~ '
            'tr>th:-soup-contains("下値目途") + td>span:nth-of-type(2)'
        )
        return str2float(value.text)

    @webpage_property
    def per_based_fair_value(self) -> Money | None:
        """PER based fair value: 理論株価(PER基準)"""
        value = self.select_one(
            'main h2:-soup-contains("想定株価レンジ") + '
            'table tr>th:-soup-contains("理論株価(PER基準)") + '
            "td>span:nth-of-type(1)"
        )
        return str2money(value.text)

    @webpage_property
    def per_fair(self) -> float | None:
        """PER when the stock price is at per_based_fair_value: 理論株価(PER基準)の時のPER"""
        value = self.select_one(
            'main h2:-soup-contains("想定株価レンジ") + '
            'table tr>th:-soup-contains("理論株価(PER基準)") + '
            "td>span:nth-of-type(2)"
        )
        return str2float(value.text)

    @webpage_property
    def per_based_ceiling(self) -> Money | None:
        """PER based ceiling price of the stock: 上値目途(PER基準)"""
        value = self.select_one(
            'main h2:-soup-contains("想定株価レンジ") + '
            'table tr:has(>th:-soup-contains("理論株価(PER基準)")) ~ '
            'tr>th:-soup-contains("上値目途") + td>span:nth-of-type(1)'
        )
        return str2money(value.text)

    @webpage_property
    def ceiling_per(self) -> float | None:
        """PER when the stock price is at per_based_ceiling: 下値目途(PER基準)の時のPER"""
        value = self.select_one(
            'main h2:-soup-contains("想定株価レンジ") + '
            'table tr:has(>th:-soup-contains("理論株価(PER基準)")) ~ '
            'tr>th:-soup-contains("上値目途") + td>span:nth-of-type(2)'
        )
        return str2float(value.text)

    @webpage_property
    def per_based_floor(self) -> Money | None:
        """PER based floor price of the stock: 下値目途(PER基準)"""
        value = self.select_one(
            'main h2:-soup-contains("想定株価レンジ") + '
            'table tr:has(>th:-soup-contains("理論株価(PER基準)")) ~ '
            'tr>th:-soup-contains("下値目途") + td>span:nth-of-type(1)'
        )
        return str2money(value.text)

    @webpage_property
    def per_floor(self) -> float | None:
        """PER when the stock price is at per_based_floor: 下値目途(PER基準)の時のPER"""
        value = self.select_one(
            'main h2:-soup-contains("想定株価レンジ") + '
            'table tr:has(>th:-soup-contains("理論株価(PER基準)")) ~ '
            'tr>th:-soup-contains("下値目途") + td>span:nth-of-type(2)'
        )
        return str2float(value.text)
