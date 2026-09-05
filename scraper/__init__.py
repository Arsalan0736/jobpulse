"""Standalone scraper package for JobPulse.

Run directly:
    python -m scraper --source=remoteok
    python -m scraper --source=arbeitnow
    python -m scraper --source=all
"""
from .base import BaseScraper, ScrapedJob

__all__ = ["BaseScraper", "ScrapedJob", "get_scraper", "list_sources"]


def __getattr__(name):
    """Lazy import of registry to avoid requiring Scrapy unless used."""
    if name in ("get_scraper", "list_sources"):
        from . import registry
        return getattr(registry, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")