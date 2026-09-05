"""CLI runner: run scrapers and push to MongoDB, then LLM-enrich."""
import argparse
import logging
import sys
import os
from pathlib import Path

from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# The standalone CLI does not initialize Django settings, so load the shared backend config here.
load_dotenv(Path(__file__).resolve().parents[1] / "backend" / ".env")

from scraper.registry import get_scraper, list_sources
from scraper.mongo_writer import upsert_jobs
from scraper.enrich import enrich_jobs

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("scraper")


def run(source: str, limit: int = 50, enrich: bool = True, delay: float = 0.5,
        country: str = "in"):
    sources = list_sources() if source == "all" else [source]
    total = 0
    for src in sources:
        logger.info("=== running %s ===", src)
        try:
            if src == "adzuna":
                from scraper.adzuna_scraper import AdzunaScraper
                scraper = AdzunaScraper(country=country)
            else:
                scraper = get_scraper(src)
        except Exception as e:
            logger.error("[%s] init failed: %s", src, e)
            continue

        jobs = scraper.run()
        if not jobs:
            logger.warning("[%s] no jobs scraped", src)
            continue

        jobs = jobs[:limit]
        logger.info("[%s] upserting %d jobs to MongoDB", src, len(jobs))
        inserted = upsert_jobs(jobs)
        total += inserted
        logger.info("[%s] inserted/updated %d new jobs", src, inserted)

        if enrich and jobs:
            logger.info("[%s] enriching with Gemini (this may take a while)", src)
            enrich_jobs(source=src, delay=delay)

    logger.info("DONE — total new/updated jobs: %d", total)
    return total


def main():
    p = argparse.ArgumentParser(description="JobPulse scraper CLI")
    p.add_argument("--source", default="all", choices=list_sources() + ["all"])
    p.add_argument("--limit", type=int, default=30, help="max jobs per source")
    p.add_argument("--no-enrich", action="store_true", help="skip LLM enrichment")
    p.add_argument("--delay", type=float, default=0.5, help="delay between LLM calls")
    p.add_argument("--country", default="in",
                   help="Adzuna country code: in, us, gb, au, de, fr, etc.")
    args = p.parse_args()
    run(args.source, args.limit, not args.no_enrich, args.delay, args.country)


if __name__ == "__main__":
    main()