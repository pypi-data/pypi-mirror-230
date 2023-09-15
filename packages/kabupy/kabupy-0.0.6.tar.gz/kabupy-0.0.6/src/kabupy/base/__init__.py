"""Base classes."""
from __future__ import annotations

from .decorators import webpage_property
from .webpage import Webpage
from .website import Website

__all__ = ["Website", "Webpage", "webpage_property"]
