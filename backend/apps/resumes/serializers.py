"""Resume serializers."""
from rest_framework import serializers
from .models import Resume


class ResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resume
        fields = [
            "id",
            "parsed_skills",
            "experience_years",
            "seniority_level",
            "summary",
            "file",
            "uploaded_at",
        ]
        read_only_fields = ["id", "uploaded_at", "parsed_skills",
                            "experience_years", "seniority_level", "summary"]