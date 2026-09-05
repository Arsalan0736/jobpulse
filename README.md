# JobPulse

AI-powered job aggregation platform. Scrapes public job feeds, runs them through Gemini for summary + skill extraction, scores them against your resume, and shows the results in a clean dark-mode UI.

```
                +--------------+      +-----------+
   Public APIs  |  scraper     | ---> |  MongoDB  |
   (RemoteOK,   |  (Beautiful- |      |  (jobs)   |
    Arbeitnow,  |   Soup +     |      +-----+-----+
    WWR)        |   Scrapy)    |            |
                +--------------+            v
                                         +---+---+
                                         |  LLM  |
                                         | (Gemini:|
                                         | summary,|
                                         | skills, |
                                         | seniority)
                                         +---+---+
                                             v
   User        +-------------+       +-----+------+
   browser --> | React (Vite)| <---> | Django/DRF | <---> MySQL
               |  Tailwind   |       |  (JWT auth)|
               +-------------+       +------------+
```

## Stack

| Layer | Tech |
|---|---|
| Frontend | React 18, Vite, Tailwind, Framer Motion, Recharts |
| Backend | Python 3.11+, Django 4.2, Django REST Framework |
| Auth | JWT (PyJWT) |
| Databases | MySQL 8 (users, saved jobs, resumes) + MongoDB 7 (raw job postings) |
| Scraping | requests + BeautifulSoup (RemoteOK, Arbeitnow), Scrapy (WeWorkRemotely) |
| LLM | Google Gemini (configured through `GEMINI_MODEL`) |
| Resume parsing | pdfplumber |

## Repo layout

```
jobpulse/
  docker-compose.yml          # MySQL + MongoDB
  .env.example                # copy to .env
  backend/                    # Django project
    manage.py                 # Django command-line entry point
    jobpulse/                 # settings
    apps/
      accounts/               # User model + auth
      jobs/                   # SavedJob model + job views
      resumes/                # Resume model + parser
      llm/                    # Gemini client + Mongo client
      management/             # Django app and scrape_jobs command
    requirements.txt
  scraper/                    # Standalone Python package
    base.py                   # BaseScraper, ScrapedJob dataclass
    remoteok_scraper.py       # requests-based
    arbeitnow_scraper.py      # requests-based
    weworkremotely_scraper.py # Scrapy-based
    mongo_writer.py           # standalone upsert
    enrich.py                 # standalone LLM enrichment
    registry.py               # source -> scraper mapping
    __main__.py               # python -m scraper CLI
  frontend/                   # Vite + React
    src/
      pages/                  # Landing, JobDetail, Resume, Saved, Analytics
      components/             # Navbar, JobCard, SearchFilters
      context/AuthContext.jsx
      api/index.js
  postman/
    jobpulse.postman_collection.json
  docs/
    architecture.md
```

## Setup

### 1. Start the databases

```bash
docker compose up -d
```

This brings up MySQL on `localhost:3307` and MongoDB on `localhost:27017`. The MySQL container listens on its internal port `3306`; host port `3307` avoids conflicts with a local MySQL installation.

### 2. Backend

```bash
cd backend
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
# macOS/Linux
cp ../.env.example .env
# Windows PowerShell
Copy-Item ..\.env.example .env
# Edit .env: set GEMINI_API_KEY, JWT_SECRET, etc.

python manage.py migrate
python manage.py createsuperuser   # optional, for /admin

# Scrape jobs and LLM-enrich
python manage.py scrape_jobs --source=all --limit=30
# or pick one source:
python manage.py scrape_jobs --source=remoteok --limit=20 --no-enrich

# Run the dev server
python manage.py runserver 0.0.0.0:8000
```

For a Linux production backend, run migrations during release and serve Django with Gunicorn instead of `runserver`:

```bash
python manage.py migrate
python manage.py collectstatic --noinput
gunicorn jobpulse.wsgi:application --bind 0.0.0.0:${PORT:-8000}
```

### 3. Run the scraper standalone (optional)

The scraper is a separate Python package and does not require Django to run. Run it from the repository root; it automatically loads `backend/.env`.

```bash
cd jobpulse
pip install -r backend/requirements.txt
# macOS/Linux (optional when backend/.env exists)
export MONGO_URI="mongodb://admin:adminpass@127.0.0.1:27017"
export MONGO_DB="jobpulse"
export GEMINI_API_KEY="your-key"
# Windows PowerShell (optional)
$env:GEMINI_API_KEY="your-key"
python -m scraper --source=all --limit=30
# or
python -m scraper --source=weworkremotely --no-enrich
```

### 4. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173.

Vite is configured to proxy `/api` requests to `http://localhost:8000`, so the frontend and backend communicate without CORS pain in dev.

## API endpoints

| Method | Path | Auth | Purpose |
|---|---|---|---|
| POST | `/api/auth/register` | none | Create user, return JWT |
| POST | `/api/auth/login` | none | Exchange credentials for JWT |
| GET  | `/api/auth/me` | JWT | Current user info |
| GET  | `/api/jobs` | none | List jobs (filters: `q`, `location`, `seniority_level`, `page`, `page_size`) |
| GET  | `/api/jobs/:id` | optional JWT | Job detail (adds `match_score` if resume uploaded) |
| POST | `/api/jobs/:id/save` | JWT | Save a job + compute match_score |
| DELETE | `/api/jobs/:id/unsave` | JWT | Remove from saved |
| GET  | `/api/saved-jobs` | JWT | Saved jobs sorted by match_score desc |
| POST | `/api/resume/upload` | JWT | multipart `file=*.pdf` |
| GET  | `/api/resume/me` | JWT | User's parsed resumes |
| GET  | `/api/analytics/trends` | none | Aggregations for the trends chart |

Send the JWT as `Authorization: Bearer <token>`.

## Postman

1. Open Postman, click **Import**.
2. Pick `postman/jobpulse.postman_collection.json`.
3. The collection uses two variables: `base_url` (default `http://localhost:8000/api`) and `token`.
4. Run **Auth → Register** or **Auth → Login** first - the test script auto-saves the JWT into `{{token}}`.
5. Walk through Jobs / Resume / Saved Jobs / Analytics in order. The **List jobs (paginated, no filters)** request auto-saves the first job id into `{{job_id}}` for use in save / detail / unsave.

Each major endpoint has both a success and a failure variant (bad password, missing file, invalid id, etc.) so you can confirm error handling.

## Scraper sources

| Source | Library | Coverage | Notes |
|---|---|---|---|
| `remoteok` | requests | Global remote | Remotive public JSON feed, free |
| `arbeitnow` | requests | EU + global | Arbeitnow public JSON API |
| `weworkremotely` | Scrapy | Global remote | WeWorkRemotely RSS feed (intentionally public) |
| `adzuna` | requests | Configurable; defaults to India (`in`) | Adzuna free-tier API. Sign up at https://developer.adzuna.com/ for `ADZUNA_APP_ID` + `ADZUNA_APP_KEY`. Change market with `--country=us`, `gb`, `de`, `au`, etc. |

Every scraper now runs descriptions through `scraper.text_clean.html_to_text` before storing, so the `description_raw` field in MongoDB is always clean plain text (not raw HTML). If you have an older Mongo with HTML still in it, run:

```bash
python -m scraper.migrate_clean_html
```

This one-shot pass rewrites every job's `description_raw` to clean text.

Each scraper upserts by URL, so re-runs are idempotent. To populate an India-heavy dataset:

```bash
python -m scraper --source=adzuna --limit=100 --country=in --no-enrich
# The Django command currently uses Adzuna's default country (`in`):
cd backend
python manage.py scrape_jobs --source=adzuna --limit=30 --no-enrich
```

## LLM enrichment

For each newly-scraped job, the enrichment pipeline calls the model configured by `GEMINI_MODEL` with a strict JSON prompt to produce:

- `description_summary` (2 sentences, plain English)
- `extracted_skills` (5-12 lowercase skill strings)
- `seniority_level` (`entry` / `mid` / `senior`)

The standalone pipeline stops retrying on invalid credentials or exhausted quota. Use `--no-enrich` when Gemini is unavailable, and provide a larger `--delay` for free-tier quotas. The same prompt is used by the standalone scraper CLI and the Django management command.

## Resume matching

1. User uploads a PDF resume (`POST /api/resume/upload`).
2. Backend extracts text with pdfplumber and falls back to PyPDF2 if needed.
3. Gemini parses the text into `parsed_skills`, `experience_years`, `seniority_level`, `summary`.
4. On `POST /api/jobs/:id/save` (and on `GET /api/jobs/:id` for authenticated users with a resume), Gemini scores the overlap between resume skills and the job's `extracted_skills` on a 0-100 scale. The score is stored on `saved_jobs.match_score` and returned with the job.

## Development notes

- **Why two databases?** Job postings are unstructured (description length, field naming, format all vary by source) so they live in MongoDB with a flexible schema. User accounts, saved-job relationships, and resumes are highly relational and need ACID, so they live in MySQL via Django ORM.
- **Scraper idempotency.** Each job's URL is unique-indexed in Mongo. Re-running the scrapers will not create duplicates; pending jobs can be enriched again after a temporary Gemini failure.
- **Rate limiting.** The scraper CLI takes a `--delay` flag (default 0.5s between LLM calls). Free-tier users should use a larger delay, such as `--delay 15`, or use `--no-enrich`.
- **Authentication.** Every protected endpoint requires a `Bearer` JWT. Tokens are issued by `/api/auth/login` and `/api/auth/register` and expire in `JWT_EXPIRY_HOURS` hours.

## Deployment checklist

- Never commit `.env` files, API keys, database passwords, JWT secrets, or uploaded media.
- Set `DJANGO_DEBUG=False`, a production `DJANGO_SECRET_KEY`, a production `JWT_SECRET`, and explicit `DJANGO_ALLOWED_HOSTS` before deployment.
- Set `CORS_ALLOWED_ORIGINS` to the deployed frontend origin instead of localhost values.
- Build the frontend with `npm run build` and serve `frontend/dist` through the chosen hosting platform or web server.
- For a separate frontend and backend deployment, set `VITE_API_BASE_URL` in `frontend/.env` to the public API URL, such as `https://api.example.com/api`. The default `/api` works when both are served from one domain through a reverse proxy.
- The included Docker Compose file is a local development setup. Use managed MySQL/MongoDB or a production container setup with persistent volumes and rotated credentials for deployment.
- Render uses the pinned Python version in `runtime.txt` because the current Gemini dependency stack is not compatible with Python 3.14. If Render still selects 3.14, add `PYTHON_VERSION=3.13.5` in the service environment variables and redeploy with a cleared build cache.

## License

MIT.
