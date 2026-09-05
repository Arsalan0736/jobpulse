# Architecture

## Data flow

```
[ public job feeds ]
  RemoteOK, Arbeitnow, WeWorkRemotely
        |
        v
[ scraper package ]      Python (requests + BS4 OR Scrapy)
        |
        |  ScrapedJob dataclass -> MongoDB upsert by URL
        v
[ MongoDB jobs collection ]
  - source, title, company, location, description_raw
  - description_summary, extracted_skills, seniority_level
        ^
        |  LLM enrichment (Gemini 1.5 Flash, JSON-mode)
[ backend/apps/llm/gemini_client.py ]
        ^
        |
[ Django REST API ]      127.0.0.1:8000
  - /api/auth/*          JWT issue + verify
  - /api/jobs            list, detail, save, unsave
  - /api/saved-jobs      sorted by match_score desc
  - /api/resume/*        upload, list (PDF -> Gemini)
  - /api/analytics       Mongo aggregations
        ^
        |  Bearer JWT in Authorization header
        v
[ React frontend ]       127.0.0.1:5173 (Vite)
  - Landing              keyword + location + seniority filters
  - JobDetail            full desc + LLM summary + skills + match badge
  - ResumeUpload         drag-drop PDF, shows extracted skills
  - SavedJobs            sorted by match_score
  - Analytics            recharts (skills, locations, volume, seniority)
        ^
        |
[ MySQL ]                users, saved_jobs (match_score), resumes (parsed_skills)
```

## MySQL schema

```sql
users
  id            PK
  email         unique
  name
  password_hash
  created_at

saved_jobs
  id            PK
  user_id       FK -> users
  job_id        string (Mongo _id, hex)
  saved_at
  match_score   int (0-100, set when saved)
  UNIQUE(user_id, job_id)

resumes
  id            PK
  user_id       FK -> users
  parsed_skills JSON
  raw_text      text
  experience_years int
  seniority_level varchar
  summary       text
  file          file (PDF, stored on disk)
  uploaded_at
```

## MongoDB schema

Collection: `jobs`

```json
{
  "_id": ObjectId,
  "source": "remoteok | arbeitnow | weworkremotely",
  "title": "Senior Backend Engineer",
  "company": "Acme",
  "location": "Remote, EU",
  "description_raw": "...",
  "description_summary": "...",   // LLM-generated
  "extracted_skills": ["python", "django", "..."],   // LLM-generated
  "seniority_level": "senior",   // LLM-classified
  "posted_date": ISODate,
  "scraped_at": ISODate,
  "url": "https://..."   // unique-indexed
}
```

Indexes:
- `url` (unique)
- `source`
- `posted_date` desc
- `extracted_skills`
- `location`
- `seniority_level`

## Scraper architecture

Each scraper subclasses `BaseScraper` and implements `fetch() -> list[ScrapedJob]`. Two concrete approaches:

- `RemoteOKScraper`, `ArbeitnowScraper` - plain `requests` + (optional) BeautifulSoup. Easy to read, easy to extend.
- `WeWorkRemotelyScraper` - Scrapy spider class wired into a `CrawlerProcess` so it runs in-process. Demonstrates framework familiarity for the "show you know Scrapy" requirement.

The `scraper.registry` maps source names to classes, so `python -m scraper --source=all` iterates through all of them. The CLI also handles MongoDB upsert and (optionally) LLM enrichment so it can be run completely standalone, no Django required.

## LLM prompts

Three prompts, all returning strict JSON:

1. `JOB_ENRICHMENT_PROMPT` - takes title/company/location/description, returns summary, skills, seniority_level.
2. `RESUME_PARSE_PROMPT` - takes raw resume text, returns skills, experience_years, seniority_level, summary.
3. `MATCH_SCORE_PROMPT` - takes two skill lists, returns integer score (0-100) and one-sentence reason.

All three live in `backend/apps/llm/gemini_client.py` and `scraper/enrich.py` (the standalone versions are kept in sync to avoid divergence).
