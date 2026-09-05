"""Quick sanity check: import every Python file and confirm structure.

Run from the backend/ directory:
    python check_imports.py
"""
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parent
sys.path.insert(0, str(BACKEND))
sys.path.insert(0, str(BACKEND.parent))

errors = []

def check_import(name):
    try:
        __import__(name)
        print(f"  OK  {name}")
    except Exception as e:
        print(f"  FAIL {name}: {e}")
        errors.append((name, e))

print("Django / apps:")
for m in [
    "jobpulse.settings",
    "jobpulse.urls",
    "apps.accounts.models",
    "apps.accounts.auth",
    "apps.accounts.views",
    "apps.accounts.serializers",
    "apps.accounts.urls",
    "apps.jobs.models",
    "apps.jobs.views",
    "apps.jobs.serializers",
    "apps.jobs.urls",
    "apps.resumes.models",
    "apps.resumes.parser",
    "apps.resumes.views",
    "apps.resumes.serializers",
    "apps.resumes.urls",
    "apps.llm.gemini_client",
    "apps.llm.mongo_client",
]:
    check_import(m)

print("\nStandalone scraper:")
for m in [
    "scraper.base",
    "scraper.registry",
    "scraper.remoteok_scraper",
    "scraper.arbeitnow_scraper",
    "scraper.weworkremotely_scraper",
    "scraper.mongo_writer",
    "scraper.enrich",
]:
    check_import(m)

print()
if errors:
    print(f"{len(errors)} import error(s).")
    sys.exit(1)
print("All imports clean.")
