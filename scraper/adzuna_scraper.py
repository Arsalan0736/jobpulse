"""Adzuna API scraper for India (and other countries, configurable).

Adzuna's free tier requires an app_id and app_key. Get them at
https://developer.adzuna.com/ - free, instant, no payment needed.

Set ADZUNA_APP_ID and ADZUNA_APP_KEY in your .env, then run:
    python -m scraper --source=adzuna
"""
import os
import requests
from datetime import datetime
from .base import BaseScraper, ScrapedJob
from .text_clean import html_to_text


def _adzuna_url(country: str = "in") -> str:
    return f"https://api.adzuna.com/v1/api/jobs/{country}/search/1"


class AdzunaScraper(BaseScraper):
    source_name = "adzuna"

    def __init__(self, country: str = "in", results_per_page: int = 50):
        self.country = country
        self.results_per_page = results_per_page

    def fetch(self) -> list[ScrapedJob]:
        app_id = os.getenv("ADZUNA_APP_ID", "")
        app_key = os.getenv("ADZUNA_APP_KEY", "")
        if not app_id or not app_key:
            raise RuntimeError(
                "Adzuna scraper requires ADZUNA_APP_ID and ADZUNA_APP_KEY. "
                "Get free keys at https://developer.adzuna.com/"
            )

        params = {
            "app_id": app_id,
            "app_key": app_key,
            "results_per_page": self.results_per_page,
            "content-type": "application/json",
        }
        # Country-specific default keyword to bias toward fresh, popular roles
        if self.country == "in":
            params["what"] = "engineer"
            params["where"] = "India"

        headers = {"User-Agent": "JobPulse/1.0 (research project)"}
        resp = requests.get(
            _adzuna_url(self.country),
            params=params,
            headers=headers,
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        items = data.get("results", [])

        results = []
        for item in items:
            try:
                url = item.get("redirect_url", "")
                if not url:
                    continue
                created = None
                if item.get("created"):
                    try:
                        created = datetime.fromisoformat(
                            item["created"].replace("Z", "+00:00")
                        )
                    except ValueError:
                        created = None

                location = item.get("location", {}).get("display_name", "") or "India"
                title = (item.get("title") or "").strip()
                company = (item.get("company", {}).get("display_name") or "").strip()
                desc_html = item.get("description", "") or ""
                desc_text = html_to_text(desc_html)

                # Adzuna's free tier often gives a snippet; fall back gracefully
                if len(desc_text) < 200:
                    desc_text = f"{title} at {company}.\n\n{desc_text}\n\nApply: {url}"

                results.append(
                    ScrapedJob(
                        source="adzuna",
                        title=title,
                        company=company,
                        location=location,
                        description_raw=desc_text[:5000],
                        url=url,
                        posted_date=created,
                        seniority_level="unknown",
                    )
                )
            except Exception:
                continue
        return results