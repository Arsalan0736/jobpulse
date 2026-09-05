"""JWT authentication for DRF."""
import jwt
from datetime import datetime, timedelta, timezone
from django.conf import settings
from rest_framework import authentication, exceptions
from .models import User


def generate_token(user):
    """Generate a JWT token for the given user."""
    payload = {
        "user_id": user.id,
        "email": user.email,
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(hours=settings.JWT_EXPIRY_HOURS),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_token(token):
    """Decode a JWT token and return the payload."""
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise exceptions.AuthenticationFailed("Token has expired")
    except jwt.InvalidTokenError:
        raise exceptions.AuthenticationFailed("Invalid token")


class JWTAuthentication(authentication.BaseAuthentication):
    """Custom DRF JWT authentication backend."""

    def authenticate(self, request):
        auth_header = request.META.get("HTTP_AUTHORIZATION", "")
        if not auth_header.startswith("Bearer "):
            return None
        token = auth_header.split("Bearer ", 1)[1]
        try:
            payload = decode_token(token)
        except exceptions.AuthenticationFailed:
            raise
        try:
            user = User.objects.get(id=payload["user_id"])
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed("User not found")
        return (user, token)

    def authenticate_header(self, request):
        return "Bearer"