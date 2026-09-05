"""Management command: python manage.py scrape_jobs --source=all"""
from django.core.management.base import BaseCommand
from apps.llm.mongo_client import get_jobs_collection
from scraper.registry import get_scraper, list_sources
from scraper.enrich import enrich_jobs


class Command(BaseCommand):
    help = "Scrape jobs from one or all sources, store in MongoDB, and LLM-enrich."

    def add_arguments(self, parser):
        parser.add_argument(
            "--source",
            default="all",
            help=f"Source to scrape. One of: {', '.join(list_sources())}, or 'all'",
        )
        parser.add_argument(
            "--limit", type=int, default=30, help="Max jobs per source"
        )
        parser.add_argument(
            "--no-enrich", action="store_true", help="Skip LLM enrichment step"
        )
        parser.add_argument(
            "--delay", type=float, default=0.5, help="Delay between LLM calls"
        )
        parser.add_argument(
            "--country",
            default="in",
            help="Adzuna country code (default 'in' for India). Examples: in, us, gb.",
        )

    def handle(self, *args, **options):
        source = options["source"]
        limit = options["limit"]
        enrich = not options["no_enrich"]
        delay = options["delay"]
        country = options["country"]

        sources = list_sources() if source == "all" else [source]
        coll = get_jobs_collection()
        total_new = 0

        for src in sources:
            self.stdout.write(self.style.NOTICE(f"=== scraping {src} ==="))
            try:
                if src == "adzuna":
                    # Country is a per-instance option for Adzuna
                    from scraper.adzuna_scraper import AdzunaScraper
                    scraper = AdzunaScraper(country=country)
                else:
                    scraper = get_scraper(src)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"[{src}] could not init: {e}"))
                continue

            jobs = scraper.run()
            if not jobs:
                self.stdout.write(self.style.WARNING(f"[{src}] no jobs scraped"))
                continue

            jobs = jobs[:limit]
            new = 0
            for j in jobs:
                doc = j.to_mongo_doc()
                result = coll.update_one(
                    {"url": doc["url"]},
                    {"$setOnInsert": doc},
                    upsert=True,
                )
                if result.upserted_id:
                    new += 1
            total_new += new
            self.stdout.write(
                self.style.SUCCESS(f"[{src}] {new} new jobs upserted "
                                   f"({len(jobs) - new} duplicates)")
            )

        if enrich and total_new > 0:
            self.stdout.write(self.style.NOTICE("=== enriching with Gemini ==="))
            for src in sources:
                enrich_jobs(source=src, delay=delay)

        self.stdout.write(
            self.style.SUCCESS(f"DONE — {total_new} new jobs total")
        )