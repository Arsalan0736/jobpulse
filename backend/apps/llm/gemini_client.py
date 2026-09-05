"""Gemini LLM client with rate limiting for JobPulse enrichment."""
import json
import time
import logging
import google.generativeai as genai
from django.conf import settings

logger = logging.getLogger(__name__)

# Configure Gemini once at import
if settings.GEMINI_API_KEY:
    genai.configure(api_key=settings.GEMINI_API_KEY)

JOB_ENRICHMENT_PROMPT = """Analyze this job posting and return ONLY valid JSON in this exact shape, no commentary:

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

RESUME_PARSE_PROMPT = """Analyze this resume and return ONLY valid JSON in this exact shape, no commentary:

{{
  "skills": ["<skill1>", "<skill2>", "..."],
  "experience_years": <integer>,
  "seniority_level": "<entry|mid|senior>",
  "summary": "<1-sentence summary of the candidate>"
}}

Rules:
- skills: 8-20 technical / role-specific skills, lowercase strings
- experience_years: total years of professional experience (integer)
- seniority_level: 'entry' (0-2 yrs), 'mid' (2-5 yrs), 'senior' (5+ yrs)
- summary: 1 sentence describing the candidate's profile

Resume text:
{resume_text}
"""

MATCH_SCORE_PROMPT = """You are a job-candidate matching scorer. Given a candidate's skills and a job's required skills, return ONLY valid JSON:

{{
  "score": <integer 0-100>,
  "reason": "<1-sentence explanation>"
}}

Scoring rules:
- 90-100: candidate has nearly all required skills
- 70-89: candidate has most required skills, missing a few
- 50-69: candidate has some relevant skills but notable gaps
- 0-49: weak overlap

Candidate skills: {resume_skills}
Job skills: {job_skills}
"""


class GeminiClient:
    """Wrapper around Gemini API with retries and rate limiting."""

    def __init__(self):
        self.model_name = settings.GEMINI_MODEL
        self.max_retries = 3
        self.base_delay = 2.0

    def _generate(self, prompt: str) -> str:
        if not settings.GEMINI_API_KEY:
            raise RuntimeError("GEMINI_API_KEY not configured")

        model = genai.GenerativeModel(self.model_name)
        for attempt in range(self.max_retries):
            try:
                # GenerationConfig is exported at top-level in some versions
                # and under genai.types in others. Try both.
                try:
                    cfg_cls = genai.types.GenerationConfig
                except AttributeError:
                    cfg_cls = genai.GenerationConfig
                response = model.generate_content(
                    prompt,
                    generation_config=cfg_cls(
                        temperature=0.2,
                        max_output_tokens=800,
                    ),
                )
                return response.text.strip()
            except Exception as e:
                logger.warning("Gemini attempt %d failed: %s", attempt + 1, e)
                if attempt < self.max_retries - 1:
                    time.sleep(self.base_delay * (2 ** attempt))
                else:
                    raise

    def _parse_json(self, text: str) -> dict:
        text = text.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        return json.loads(text)

    def enrich_job(self, title: str, company: str, location: str, description: str) -> dict:
        """Generate summary, skills, and seniority level for a job posting."""
        desc_truncated = description[:3000] if description else ""
        prompt = JOB_ENRICHMENT_PROMPT.format(
            title=title or "Unknown",
            company=company or "Unknown",
            location=location or "Unknown",
            description=desc_truncated,
        )
        try:
            text = self._generate(prompt)
            result = self._parse_json(text)
            return {
                "summary": result.get("summary", ""),
                "skills": result.get("skills", []),
                "seniority_level": result.get("seniority_level", "mid"),
            }
        except Exception as e:
            logger.error("Job enrichment failed for %s: %s", title, e)
            return {
                "summary": f"{title} at {company}. See full description for details.",
                "skills": [],
                "seniority_level": "mid",
            }

    def parse_resume(self, resume_text: str) -> dict:
        """Extract structured info from a resume."""
        prompt = RESUME_PARSE_PROMPT.format(resume_text=resume_text[:4000])
        try:
            text = self._generate(prompt)
            return self._parse_json(text)
        except Exception as e:
            logger.error("Resume parsing failed: %s", e)
            return {
                "skills": [],
                "experience_years": 0,
                "seniority_level": "entry",
                "summary": "",
            }

    def match_score(self, resume_skills: list, job_skills: list) -> dict:
        """Compute match score between resume skills and job skills."""
        if not resume_skills or not job_skills:
            return {"score": 0, "reason": "Insufficient skill data."}
        prompt = MATCH_SCORE_PROMPT.format(
            resume_skills=", ".join(resume_skills),
            job_skills=", ".join(job_skills),
        )
        try:
            text = self._generate(prompt)
            result = self._parse_json(text)
            score = max(0, min(100, int(result.get("score", 0))))
            return {"score": score, "reason": result.get("reason", "")}
        except Exception as e:
            logger.error("Match scoring failed: %s", e)
            overlap = set(s.lower() for s in resume_skills) & set(s.lower() for s in job_skills)
            score = int((len(overlap) / max(len(job_skills), 1)) * 100)
            return {"score": score, "reason": "Computed via skill overlap."}


def enrich_batch(jobs: list, delay: float = 0.5) -> list:
    """Enrich a list of job dicts with rate-limited Gemini calls."""
    client = GeminiClient()
    enriched = []
    for i, job in enumerate(jobs):
        try:
            enrichment = client.enrich_job(
                title=job.get("title", ""),
                company=job.get("company", ""),
                location=job.get("location", ""),
                description=job.get("description_raw", ""),
            )
            job.update(enrichment)
            enriched.append(job)
            if i < len(jobs) - 1:
                time.sleep(delay)
        except Exception as e:
            logger.error("Batch enrichment failed for %s: %s", job.get("url"), e)
            continue
    return enriched