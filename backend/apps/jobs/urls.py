"""URLs for jobs app."""
from django.urls import path
from .views import (
    JobListView,
    JobDetailView,
    SaveJobView,
    UnsaveJobView,
    SavedJobsView,
    AnalyticsTrendsView,
)

urlpatterns = [
    path("jobs", JobListView.as_view(), name="jobs-list"),
    path("jobs/<str:job_id>", JobDetailView.as_view(), name="jobs-detail"),
    path("jobs/<str:job_id>/save", SaveJobView.as_view(), name="jobs-save"),
    path("jobs/<str:job_id>/unsave", UnsaveJobView.as_view(), name="jobs-unsave"),
    path("saved-jobs", SavedJobsView.as_view(), name="saved-jobs"),
    path("analytics/trends", AnalyticsTrendsView.as_view(), name="analytics-trends"),
]