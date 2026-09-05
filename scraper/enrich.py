"""Standalone LLM enrichment for scraped jobs (no Django)."""
import os
import time
import logging
import json
from pymongo import MongoClient, ASCENDING
from pymongo.errors import ConnectionFailure

logger = logging.getLogger(__name__)


class GeminiAuthError(RuntimeError):
    """The configured Gemini credential cannot be used."""


class GeminiQuotaError(RuntimeError):
    """The Gemini project has exhausted its request quota."""

_MONGO_URI = os.getenv("MONGO_URI", "mongodb://admin:adminpass@127.0.0.1:27017")
_MONGO_DB = os.getenv("MONGO_DB", "jobpulse")
_GEMINI_KEY = os.getenv("GEMINI_API_KEY", "")
_GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

ENRICHMENT_PROMPT = """Analyze this job posting and return ONLY valid JSON in this exact shape, no commentary:

{{
  "summary": "<2-sentence plain-English summary of the role>",
  "skills": ["<skill1>", "<skill2>", "..."],
  "seniority_level": "<entry|mid|senior>"
}}

Rules:
- summary: 2 sentences, no buzzwords, plain English, what the person will actually do
- skills: 5-12 technical / role-specific skills, lowercase strings, no duplicates
- seniority_level: 'entry' for 0-2 yrs, 'mid' for 2-5 yrs, 'senior' for 5+ yrs

Job title: {title}
Company: {company}
Location: {location}
Description: {description}
"""


def _call_gemini(prompt: str) -> str:
    if not _GEMINI_KEY:
        raise RuntimeError("GEMINI_API_KEY not set in env")
    import google.generativeai as genai
    genai.configure(api_key=_GEMINI_KEY)
    model = genai.GenerativeModel(_GEMINI_MODEL)
    for attempt in range(3):
        try:
            try:
                cfg_cls = genai.types.GenerationConfig
            except AttributeError:
                cfg_cls = genai.GenerationConfig
            resp = model.generate_content(
                prompt,
                generation_config=cfg_cls(temperature=0.2, max_output_tokens=800),
            )
            return resp.text.strip()
        except Exception as e:
            error_text = str(e).lower()
            if "403" in error_text or "reported as leaked" in error_text:
                raise GeminiAuthError(
                    "Gemini API key was rejected. Create a new key and update GEMINI_API_KEY."
                ) from e
            if "429" in error_text or "quota" in error_text:
                raise GeminiQuotaError(
                    "Gemini API quota exceeded. Wait for the quota window to reset or use another project."
                ) from e
            logger.warning("Gemini attempt %d failed: %s", attempt + 1, e)
            if attempt < 2:
                time.sleep(2 ** attempt)
            else:
                raise


def _parse_json(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    return json.loads(text)


def enrich_one(doc: dict) -> dict:
    """Enrich a single Mongo job doc in place."""
    desc = (doc.get("description_raw") or "")[:3000]
    prompt = ENRICHMENT_PROMPT.format(
        title=doc.get("title", ""),
        company=doc.get("company", ""),
        location=doc.get("location", ""),
        description=desc,
    )
    try:
        text = _call_gemini(prompt)
        result = _parse_json(text)
        return {
            "description_summary": result.get("summary", ""),
            "extracted_skills": result.get("skills", []),
            "seniority_level": result.get("seniority_level", "mid"),
        }
    except (GeminiAuthError, GeminiQuotaError):
        raise
    except Exception as e:
        logger.error("Enrichment failed for %s: %s", doc.get("url"), e)
        return {
            "description_summary": f"{doc.get('title','')} at {doc.get('company','')}.",
            "extracted_skills": [],
            "seniority_level": "mid",
        }


def enrich_jobs(source: str = None, delay: float = 0.5, batch_size: int = 100) -> int:
    """Find un-enriched jobs and enrich them. Returns count enriched."""
    client = MongoClient(_MONGO_URI, serverSelectionTimeoutMS=5000)
    coll = client[_MONGO_DB]["jobs"]
    query = {"$or": [
        {"description_summary": {"$in": ["", None]}},
        {"extracted_skills": {"$size": 0}},
    ]}
    if source:
        query["source"] = source
    cursor = coll.find(query).limit(batch_size)

    count = 0
    for doc in cursor:
        try:
            enrichment = enrich_one(doc)
        except (GeminiAuthError, GeminiQuotaError) as e:
            logger.error("Stopping enrichment: %s", e)
            break
        coll.update_one({"_id": doc["_id"]}, {"$set": enrichment})
        count += 1
        logger.info("enriched %d/%d: %s @ %s", count, batch_size,
                    doc.get("title", ""), doc.get("company", ""))
        if count < batch_size:
            time.sleep(delay)
    logger.info("DONE — enriched %d jobs", count)
    return count