"""Resume views: upload + retrieve."""
import logging
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.files.base import ContentFile
from .models import Resume
from .parser import extract_text_from_pdf
from .serializers import ResumeSerializer
from apps.llm.gemini_client import GeminiClient

logger = logging.getLogger(__name__)


class ResumeUploadView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        upload = request.FILES.get("file")
        if upload is None:
            return Response(
                {"detail": "No file provided. Use 'file' form field."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not upload.name.lower().endswith(".pdf"):
            return Response(
                {"detail": "Only PDF files are supported."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        upload.seek(0)
        raw_text = extract_text_from_pdf(upload)
        if not raw_text:
            return Response(
                {"detail": "Could not extract text from PDF. File may be image-only."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        upload.seek(0)
        try:
            client = GeminiClient()
            parsed = client.parse_resume(raw_text)
        except Exception as e:
            logger.error("Resume parsing LLM failed: %s", e)
            parsed = {"skills": [], "experience_years": 0,
                      "seniority_level": "entry", "summary": ""}

        resume = Resume.objects.create(
            user=request.user,
            parsed_skills=parsed.get("skills", []),
            raw_text=raw_text[:20000],
            experience_years=parsed.get("experience_years", 0),
            seniority_level=parsed.get("seniority_level", "entry"),
            summary=parsed.get("summary", ""),
            file=upload,
        )
        return Response(ResumeSerializer(resume).data, status=status.HTTP_201_CREATED)


class ResumeMeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        resumes = Resume.objects.filter(user=request.user).order_by("-uploaded_at")
        return Response({
            "count": resumes.count(),
            "results": ResumeSerializer(resumes, many=True).data,
        })