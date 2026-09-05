"""Scraper registry - maps source names to scraper instances."""
import importlib

_REGISTRY = {}


def _load():
    """Build the registry lazily so missing optional deps don't break imports."""
    global _REGISTRY
    if _REGISTRY:
        return _REGISTRY
    sources = {
        "remoteok": "scraper.remoteok_scraper.RemoteOKScraper",
        "arbeitnow": "scraper.arbeitnow_scraper.ArbeitnowScraper",
        "weworkremotely": "scraper.weworkremotely_scraper.WeWorkRemotelyScraper",
        "adzuna": "scraper.adzuna_scraper.AdzunaScraper",
    }
    for name, path in sources.items():
        try:
            module_path, cls_name = path.rsplit(".", 1)
            module = importlib.import_module(module_path)
            _REGISTRY[name] = getattr(module, cls_name)
        except Exception:
            # Optional dep (e.g. Scrapy) not installed; skip silently
            pass
    return _REGISTRY


def list_sources() -> list[str]:
    return list(_load().keys())


def get_scraper(name: str):
    cls = _load().get(name.lower())
    if cls is None:
        available = list_sources()
        raise ValueError(
            f"Unknown or unavailable scraper: {name}. Available: {available}"
        )
    return cls()