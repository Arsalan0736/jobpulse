"""MySQL models for saved_jobs."""
from django.conf import settings
from django.db import models


class SavedJob(models.Model):
    """A job that a user has saved (Mongo _id referenced as string)."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="saved_jobs",
    )
    job_id = models.CharField(max_length=64, db_index=True)
    saved_at = models.DateTimeField(auto_now_add=True)
    match_score = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = "saved_jobs"
        unique_together = [("user", "job_id")]
        ordering = ["-match_score", "-saved_at"]

    def __str__(self):
        return f"{self.user.email} -> {self.job_id}"