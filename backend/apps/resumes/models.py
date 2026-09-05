"""Resume model stored in MySQL."""
from django.conf import settings
from django.db import models


class Resume(models.Model):
    """Parsed resume for a user."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="resumes",
    )
    parsed_skills = models.JSONField(default=list)
    raw_text = models.TextField(blank=True)
    experience_years = models.IntegerField(default=0)
    seniority_level = models.CharField(max_length=32, default="entry")
    summary = models.TextField(blank=True)
    file = models.FileField(upload_to="resumes/", null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "resumes"
        ordering = ["-uploaded_at"]

    def __str__(self):
        return f"{self.user.email} resume @ {self.uploaded_at:%Y-%m-%d %H:%M}"