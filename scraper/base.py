"""Base classes for scrapers."""
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional
import logging

logger = logging.getLogger(__name__)


@dataclass
class ScrapedJob:
    """A raw scraped job, before LLM enrichment."""
    source: str
    title: str
    company: str
    location: str
    description_raw: str
    url: str
    posted_date: Optional[datetime] = None
    seniority_level: str = "unknown"

    def to_mongo_doc(self) -> dict:
        """Convert to a MongoDB-ready dict."""
        doc = asdict(self)
        doc["scraped_at"] = datetime.utcnow()
        doc["description_summary"] = ""
        doc["extracted_skills"] = []
        return doc


class BaseScraper:
    """Abstract base class for all scrapers."""

    source_name: str = "base"

    def fetch(self) -> list[ScrapedJob]:
        """Fetch and parse jobs. Returns list of ScrapedJob."""
        raise NotImplementedError

    def run(self) -> list[ScrapedJob]:
        """Run the scraper and log results."""
        logger.info("[%s] starting scrape", self.source_name)
        try:
            jobs = self.fetch()
            logger.info("[%s] scraped %d jobs", self.source_name, len(jobs))
            return jobs
        except Exception as e:
            logger.error("[%s] scrape failed: %s", self.source_name, e)
            return []