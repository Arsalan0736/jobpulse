"""MongoDB client wrapper for JobPulse."""
import logging
from typing import Optional
from django.conf import settings
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import ConnectionFailure

logger = logging.getLogger(__name__)

_client: Optional[MongoClient] = None


def get_client() -> MongoClient:
    """Get or create the MongoDB client singleton."""
    global _client
    if _client is None:
        try:
            _client = MongoClient(settings.MONGO_URI, serverSelectionTimeoutMS=5000)
            _client.admin.command("ping")
            logger.info("MongoDB connection established")
        except ConnectionFailure as e:
            logger.error("MongoDB connection failed: %s", e)
            raise
    return _client


def get_db():
    """Get the JobPulse MongoDB database."""
    return get_client()[settings.MONGO_DB]


def get_jobs_collection():
    """Get the jobs collection with indexes."""
    db = get_db()
    jobs = db["jobs"]
    jobs.create_index([("url", ASCENDING)], unique=True)
    jobs.create_index([("source", ASCENDING)])
    jobs.create_index([("posted_date", DESCENDING)])
    jobs.create_index([("extracted_skills", ASCENDING)])
    jobs.create_index([("location", ASCENDING)])
    jobs.create_index([("seniority_level", ASCENDING)])
    return jobs


def close_client():
    """Close the MongoDB client (for management commands / tests)."""
    global _client
    if _client is not None:
        _client.close()
        _client = None