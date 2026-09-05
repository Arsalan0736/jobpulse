"""API URL root."""
from django.urls import path, include


urlpatterns = [
    path("auth/", include("apps.accounts.urls")),
    path("", include("apps.jobs.urls")),
    path("", include("apps.resumes.urls")),
]