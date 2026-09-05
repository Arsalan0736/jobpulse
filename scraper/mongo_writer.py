"""Mongo writer for standalone scraper usage (no Django)."""
import os
import logging
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import ConnectionFailure

logger = logging.getLogger(__name__)

_MONGO_URI = os.getenv("MONGO_URI", "mongodb://admin:adminpass@127.0.0.1:27017")
_MONGO_DB = os.getenv("MONGO_DB", "jobpulse")
_client = None


def _client_lazy():
    global _client
    if _client is None:
        _client = MongoClient(_MONGO_URI, serverSelectionTimeoutMS=5000)
        _client.admin.command("ping")
        # ensure indexes
        jobs = _client[_MONGO_DB]["jobs"]
        jobs.create_index([("url", ASCENDING)], unique=True)
        jobs.create_index([("source", ASCENDING)])
        jobs.create_index([("posted_date", DESCENDING)])
        jobs.create_index([("extracted_skills", ASCENDING)])
        jobs.create_index([("location", ASCENDING)])
        jobs.create_index([("seniority_level", ASCENDING)])
    return _client


def upsert_jobs(jobs) -> int:
    """Upsert a list of ScrapedJob into Mongo. Returns count of new jobs."""
    if not jobs:
        return 0
    coll = _client_lazy()[_MONGO_DB]["jobs"]
    new_count = 0
    for j in jobs:
        doc = j.to_mongo_doc()
        result = coll.update_one(
            {"url": doc["url"]},
            {"$setOnInsert": doc},
            upsert=True,
        )
        if result.upserted_id:
            new_count += 1
    return new_count