"""Serializers for saved jobs."""
from rest_framework import serializers
from .models import SavedJob


class SavedJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedJob
        fields = ["id", "job_id", "saved_at", "match_score"]
        read_only_fields = ["id", "saved_at"]