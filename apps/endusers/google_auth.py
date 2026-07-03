"""Google OAuth authentication utilities."""

from django.conf import settings
from google.auth.transport import requests
from google.oauth2 import id_token


def verify_google_token(token: str) -> dict:
    """
    Verify a Google OAuth ID token using GOOGLE_CLIENT_ID from settings.

    Returns:
        dict: User information extracted from the token.

    Raises:
        ValueError: If the token is invalid or GOOGLE_CLIENT_ID is not set.
    """
    client_id = getattr(settings, "GOOGLE_CLIENT_ID", None)
    if not client_id:
        raise ValueError("GOOGLE_CLIENT_ID is not configured in settings")

    try:
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), client_id)
        return {
            "email": idinfo.get("email"),
            "email_verified": idinfo.get("email_verified", False),
            "name": idinfo.get("name", ""),
            "given_name": idinfo.get("given_name", ""),
            "family_name": idinfo.get("family_name", ""),
            "picture": idinfo.get("picture", ""),
            "sub": idinfo.get("sub"),
        }
    except ValueError as e:
        import traceback
        traceback.print_exc()
        raise ValueError(f"Invalid Google token: {str(e)}")
