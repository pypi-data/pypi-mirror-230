"""util functions"""
from __future__ import annotations

import re

from money import Money

__all__ = ["str2money", "str2float"]

jpy_unit = str.maketrans({"百": "0" * 2, "千": "0" * 3, "万": "0" * 4, "億": "0" * 8})


def str2money(price: str) -> Money | None:
    """Convert str to JPY Money object"""
    if not re.search(r"\d", price):
        return None
    amount = price.translate(jpy_unit)
    amount = re.sub(r"[^\d.-]", "", amount)
    if amount == "":
        return None
    return Money(amount, "JPY")


def str2float(value: str) -> float | None:
    """Convert str to float"""
    if not re.search(r"\d", value):
        return None
    amount = re.sub(r"[^\d.-]", "", value)
    if amount == "":
        return None
    return float(amount)


def str2int(value: str) -> int | None:
    """Convert str to int"""
    if not re.search(r"\d", value):
        return None
    amount = re.sub(r"[^\d.-]", "", value)
    if amount == "":
        return None
    return int(amount)
