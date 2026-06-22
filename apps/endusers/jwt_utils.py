from datetime import datetime, timedelta, timezone

import jwt
from django.conf import settings

from .models import EndUser

# JWT Configuration
JWT_SECRET = getattr(settings, "JWT_SECRET", settings.SECRET_KEY)
JWT_ALGORITHM = getattr(settings, "JWT_ALGORITHM", "HS256")
JWT_EXPIRATION_HOURS = getattr(settings, "JWT_EXPIRATION_HOURS", 24)
JWT_REFRESH_EXPIRATION_DAYS = getattr(settings, "JWT_REFRESH_EXPIRATION_DAYS", 30)


def generate_token(user: EndUser) -> str:
    """
    Generate JWT token for an EndUser.

    Payload contains:
    - id: User UUID
    - mobile: User's mobile number
    - created_at: User's creation timestamp
    - exp: Token expiration time
    - iat: Token issued at time
    """
    now = datetime.now(timezone.utc)
    payload = {
        "id": str(user.id),
        "mobile": user.mobile,
        "created_at": user.created_at.isoformat(),
        "exp": now + timedelta(hours=JWT_EXPIRATION_HOURS),
        "iat": now,
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> dict | None:
    """
    Decode and validate JWT token.

    Returns payload dict if valid, None if invalid or expired.
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def get_user_from_token(token: str) -> EndUser | None:
    """
    Get EndUser instance from JWT token.

    Returns EndUser if token is valid and user exists, None otherwise.
    """
    payload = decode_token(token)
    if not payload:
        return None

    try:
        user = EndUser.objects.get(id=payload["id"])
        return user
    except EndUser.DoesNotExist:
        return None


def generate_refresh_token(user: EndUser) -> str:
    """
    Generate refresh token for an EndUser.

    Refresh tokens have longer expiration (30 days by default).

    Payload contains:
    - id: User UUID
    - type: Token type (refresh)
    - exp: Token expiration time
    - iat: Token issued at time
    """
    now = datetime.now(timezone.utc)
    payload = {
        "id": str(user.id),
        "type": "refresh",
        "exp": now + timedelta(days=JWT_REFRESH_EXPIRATION_DAYS),
        "iat": now,
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_refresh_token(token: str) -> dict | None:
    """
    Decode and validate refresh token.

    Returns payload dict if valid refresh token, None if invalid/expired/wrong type.
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        # Verify it's a refresh token
        if payload.get("type") != "refresh":
            return None
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def generate_tokens(user: EndUser) -> dict:
    """
    Generate both access and refresh tokens for a user.

    Returns:
        dict: {
            "access_token": str,
            "refresh_token": str
        }
    """
    return {
        "access_token": generate_token(user),
        "refresh_token": generate_refresh_token(user),
    }
