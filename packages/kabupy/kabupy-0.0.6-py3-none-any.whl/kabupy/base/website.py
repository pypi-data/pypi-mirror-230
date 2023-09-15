"""Base class for website"""
from __future__ import annotations

from abc import ABC, abstractmethod


class Website(ABC):
    """Base class for website"""

    @abstractmethod
    def __init__(self):
        self.url: str
