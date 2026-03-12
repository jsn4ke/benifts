"""银行理财产品爬虫模块"""

from .base import BaseScraper
from .cmb import CMBScraper
from .shbank import SHBankScraper

__all__ = ["BaseScraper", "CMBScraper", "SHBankScraper"]
