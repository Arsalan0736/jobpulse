"""RemoteOK scraper using their public JSON API.

RemoteOK exposes jobs at https://remotive.com/api and is an LLM-friendly public
job feed. We use the RemoteOK /api endpoint which returns JSON and is intended
for programmatic consumption.
"""
import requests
from datetime import datetime
from .base import BaseScraper, ScrapedJob
from .text_clean import html_to_text

REMOTEOK_API = "https://remotive.com/api/remote-jobs"


class RemoteOKScraper(BaseScraper):
    source_name = "remoteok"

    def fetch(self) -> list[ScrapedJob]:
        headers = {"User-Agent": "JobPulse/1.0 (research project)"}
        resp = requests.get(REMOTEOK_API, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        jobs_raw = data.get("jobs", [])
        results = []
        for item in jobs_raw[:50]:
            try:
                posted = None
                if item.get("publication_date"):
                    posted = datetime.fromisoformat(
                        item["publication_date"].replace("Z", "+00:00")
                    )
                url = item.get("url", "")
                if not url:
                    continue
                results.append(
                    ScrapedJob(
                        source="remoteok",
                        title=item.get("title", "").strip(),
                        company=item.get("company_name", "").strip(),
                        location=", ".join(item.get("candidate_required_location", []) if isinstance(item.get("candidate_required_location"), list) else [item.get("candidate_required_location") or ""]) or "Remote",
                        description_raw=html_to_text(item.get("description") or "")[:5000],
                        url=url,
                        posted_date=posted,
                        seniority_level="unknown",
                    )
                )
            except Exception:
                continue
        return results