"""ASGI config for JobPulse."""
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "jobpulse.settings")
application = get_asgi_application()