"""Scrapy-based scraper for WeWorkRemotely RSS feed.

This demonstrates the Scrapy framework approach. The feed is a public RSS
job board that explicitly invites syndication.
"""
import scrapy
from scrapy.crawler import CrawlerProcess
from datetime import datetime
from .base import BaseScraper, ScrapedJob
from .text_clean import html_to_text

WWR_RSS = "https://weworkremotely.com/categories/remote-programming-jobs.rss"


class WWRSpider(scrapy.Spider):
    name = "wwr"
    start_urls = [WWR_RSS]
    custom_settings = {
        "ROBOTSTXT_OBEY": True,
        "USER_AGENT": "JobPulse/1.0 (+https://example.com)",
        "LOG_LEVEL": "WARNING",
        "DOWNLOAD_TIMEOUT": 30,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.results: list[ScrapedJob] = []

    def parse(self, response):
        for item in response.css("item"):
            link = item.css("link::text").get() or ""
            title = item.css("title::text").get() or ""
            desc = item.css("description::text").get() or ""
            pub = item.css("pubDate::text").get() or ""
            if not link:
                continue
            posted = None
            for fmt in ("%a, %d %b %Y %H:%M:%S %z", "%a, %d %b %Y %H:%M:%S GMT"):
                try:
                    posted = datetime.strptime(pub.strip(), fmt)
                    break
                except ValueError:
                    continue

            parts = title.split(":", 1)
            company = parts[0].strip() if parts else "Unknown"
            role = parts[1].strip() if len(parts) > 1 else title.strip()

            self.results.append(
                ScrapedJob(
                    source="weworkremotely",
                    title=role,
                    company=company,
                    location="Remote",
                    description_raw=html_to_text(desc)[:5000],
                    url=link,
                    posted_date=posted,
                    seniority_level="unknown",
                )
            )


class WeWorkRemotelyScraper(BaseScraper):
    source_name = "weworkremotely"

    def fetch(self) -> list[ScrapedJob]:
        jobs: list[ScrapedJob] = []
        process = CrawlerProcess(settings={
            "ROBOTSTXT_OBEY": True,
            "USER_AGENT": "JobPulse/1.0",
            "LOG_LEVEL": "ERROR",
        })
        spider = WWRSpider()
        process.crawl(spider)
        process.start()

        # spider.results is populated by our monkey-patch below
        jobs = getattr(spider, "results", [])
        return jobs