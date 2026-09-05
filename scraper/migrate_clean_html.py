"""One-shot migration: re-sanitize description_raw on every job in Mongo.

Useful after switching scrapers to use html_to_text. Existing records may
still have raw HTML.

Run from the project root (where the scraper/ folder lives):
    python -m scraper.migrate_clean_html
"""
import os
import sys
import logging
from pymongo import MongoClient

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scraper.text_clean import html_to_text

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("migrate")

_MONGO_URI = os.getenv("MONGO_URI", "mongodb://admin:adminpass@127.0.0.1:27017")
_MONGO_DB = os.getenv("MONGO_DB", "jobpulse")


def main():
    coll = MongoClient(_MONGO_URI, serverSelectionTimeoutMS=5000)[_MONGO_DB]["jobs"]
    cursor = coll.find({"description_raw": {"$exists": True, "$ne": ""}})
    total = 0
    updated = 0
    for doc in cursor:
        total += 1
        raw = doc.get("description_raw", "") or ""
        if "<" not in raw and "&lt;" not in raw:
            continue
        cleaned = html_to_text(raw)[:5000]
        if cleaned != raw:
            coll.update_one({"_id": doc["_id"]}, {"$set": {"description_raw": cleaned}})
            updated += 1
            if updated % 25 == 0:
                logger.info("cleaned %d / %d", updated, total)
    logger.info("DONE — scanned %d, cleaned %d", total, updated)


if __name__ == "__main__":
    main()