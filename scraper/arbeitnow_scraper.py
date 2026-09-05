"""Arbeitnow public API scraper."""
import requests
from datetime import datetime
from .base import BaseScraper, ScrapedJob
from .text_clean import html_to_text

ARBEITNOW_API = "https://arbeitnow.com/api/job-board-api"


class ArbeitnowScraper(BaseScraper):
    source_name = "arbeitnow"

    def fetch(self) -> list[ScrapedJob]:
        headers = {"User-Agent": "JobPulse/1.0 (research project)"}
        resp = requests.get(ARBEITNOW_API, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        jobs_raw = data.get("data", [])
        results = []
        for item in jobs_raw[:50]:
            try:
                url = item.get("url", "")
                if not url:
                    continue
                posted = None
                if item.get("created_at"):
                    try:
                        posted = datetime.fromtimestamp(int(item["created_at"]))
                    except (ValueError, TypeError):
                        posted = None
                seniority = "unknown"
                tags = " ".join(item.get("tags", [])).lower()
                if "senior" in tags or "lead" in tags:
                    seniority = "senior"
                elif "junior" in tags or "entry" in tags:
                    seniority = "entry"
                results.append(
                    ScrapedJob(
                        source="arbeitnow",
                        title=item.get("title", "").strip(),
                        company=item.get("company_name", "").strip(),
                        location=item.get("location", "").strip() or "Unspecified",
                        description_raw=html_to_text(item.get("description") or "")[:5000],
                        url=url,
                        posted_date=posted,
                        seniority_level=seniority,
                    )
                )
            except Exception:
                continue
        return results