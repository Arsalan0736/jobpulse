"""Job views: list, detail, save, saved-jobs dashboard, analytics."""
import logging
from bson import ObjectId
from bson.errors import InvalidId
from django.shortcuts import get_object_or_404
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import NotFound
from apps.llm.mongo_client import get_jobs_collection
from apps.resumes.models import Resume
from apps.llm.gemini_client import GeminiClient
from .models import SavedJob
from .serializers import SavedJobSerializer

logger = logging.getLogger(__name__)


def _serialize_job(doc: dict) -> dict:
    """Convert MongoDB doc to JSON-friendly dict."""
    return {
        "id": str(doc["_id"]),
        "source": doc.get("source", ""),
        "title": doc.get("title", ""),
        "company": doc.get("company", ""),
        "location": doc.get("location", ""),
        "url": doc.get("url", ""),
        "description_raw": doc.get("description_raw", ""),
        "description_summary": doc.get("description_summary", ""),
        "extracted_skills": doc.get("extracted_skills", []),
        "posted_date": doc.get("posted_date").isoformat() if doc.get("posted_date") else None,
        "scraped_at": doc.get("scraped_at").isoformat() if doc.get("scraped_at") else None,
        "seniority_level": doc.get("seniority_level", "mid"),
    }


def _get_job_or_404(job_id: str):
    """Fetch a job by Mongo _id string or raise NotFound."""
    try:
        oid = ObjectId(job_id)
    except (InvalidId, TypeError):
        raise NotFound("Invalid job id")
    doc = get_jobs_collection().find_one({"_id": oid})
    if doc is None:
        raise NotFound("Job not found")
    return doc


class JobListView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        page = int(request.query_params.get("page", 1))
        page_size = min(int(request.query_params.get("page_size", 20)), 100)
        location = request.query_params.get("location", "").strip()
        seniority = request.query_params.get("seniority_level", "").strip()
        keyword = request.query_params.get("q", "").strip()

        query = {}
        if location:
            query["location"] = {"$regex": location, "$options": "i"}
        if seniority in ("entry", "mid", "senior"):
            query["seniority_level"] = seniority
        if keyword:
            query["$or"] = [
                {"title": {"$regex": keyword, "$options": "i"}},
                {"company": {"$regex": keyword, "$options": "i"}},
                {"description_summary": {"$regex": keyword, "$options": "i"}},
            ]

        coll = get_jobs_collection()
        total = coll.count_documents(query)
        cursor = (
            coll.find(query)
            .sort("posted_date", -1)
            .skip((page - 1) * page_size)
            .limit(page_size)
        )
        results = [_serialize_job(doc) for doc in cursor]
        return Response({
            "count": total,
            "page": page,
            "page_size": page_size,
            "results": results,
        })


class JobDetailView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, job_id):
        doc = _get_job_or_404(job_id)
        job = _serialize_job(doc)

        # If user authenticated and has a resume, compute match score
        match_score = None
        if request.user.is_authenticated:
            resume = Resume.objects.filter(user=request.user).order_by("-uploaded_at").first()
            if resume and resume.parsed_skills and doc.get("extracted_skills"):
                client = GeminiClient()
                result = client.match_score(resume.parsed_skills, doc["extracted_skills"])
                match_score = result["score"]
        job["match_score"] = match_score
        return Response(job)


class SaveJobView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, job_id):
        doc = _get_job_or_404(job_id)
        job_skills = doc.get("extracted_skills", [])
        match_score = None

        resume = Resume.objects.filter(user=request.user).order_by("-uploaded_at").first()
        if resume and resume.parsed_skills and job_skills:
            client = GeminiClient()
            result = client.match_score(resume.parsed_skills, job_skills)
            match_score = result["score"]

        saved, created = SavedJob.objects.update_or_create(
            user=request.user,
            job_id=job_id,
            defaults={"match_score": match_score},
        )
        return Response(
            {
                "saved": True,
                "created": created,
                "match_score": match_score,
                "saved_job": SavedJobSerializer(saved).data,
            },
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class UnsaveJobView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, job_id):
        deleted, _ = SavedJob.objects.filter(user=request.user, job_id=job_id).delete()
        if deleted == 0:
            return Response({"detail": "Not saved."}, status=status.HTTP_404_NOT_FOUND)
        return Response({"unsaved": True}, status=status.HTTP_200_OK)


class SavedJobsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        saved = SavedJob.objects.filter(user=request.user).order_by("-match_score", "-saved_at")
        results = []
        for s in saved:
            try:
                doc = _get_job_or_404(s.job_id)
                job = _serialize_job(doc)
                job["match_score"] = s.match_score
                job["saved_at"] = s.saved_at.isoformat()
                results.append(job)
            except NotFound:
                continue
        return Response({"count": len(results), "results": results})


class AnalyticsTrendsView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        coll = get_jobs_collection()
        pipeline_skills = [
            {"$unwind": "$extracted_skills"},
            {"$group": {"_id": "$extracted_skills", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 20},
        ]
        skills = [{"skill": d["_id"], "count": d["count"]}
                  for d in coll.aggregate(pipeline_skills)]

        pipeline_location = [
            {"$group": {"_id": "$location", "count": {"$sum": 1}}},
            {"$match": {"_id": {"$nin": ["", None]}}},
            {"$sort": {"count": -1}},
            {"$limit": 15},
        ]
        locations = [{"location": d["_id"] or "Unspecified", "count": d["count"]}
                     for d in coll.aggregate(pipeline_location)]

        pipeline_seniority = [
            {"$group": {"_id": "$seniority_level", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
        ]
        seniority = [{"level": d["_id"] or "unspecified", "count": d["count"]}
                     for d in coll.aggregate(pipeline_seniority)]

        pipeline_volume = [
            {"$group": {
                "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$scraped_at"}},
                "count": {"$sum": 1},
            }},
            {"$sort": {"_id": 1}},
            {"$limit": 30},
        ]
        volume = [{"date": d["_id"], "count": d["count"]}
                  for d in coll.aggregate(pipeline_volume)]

        return Response({
            "top_skills": skills,
            "top_locations": locations,
            "seniority_breakdown": seniority,
            "posting_volume": volume,
            "total_jobs": coll.count_documents({}),
        })