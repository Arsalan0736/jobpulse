"""URLs for resumes app."""
from django.urls import path
from .views import ResumeUploadView, ResumeMeView

urlpatterns = [
    path("resume/upload", ResumeUploadView.as_view(), name="resume-upload"),
    path("resume/me", ResumeMeView.as_view(), name="resume-me"),
]