"""Google OAuth authentication utilities."""

from google.auth.transport import requests
from google.oauth2 import id_token


def verify_google_token(token: str, client_id: str = None) -> dict:
    """
    Verify a Google OAuth token and return user information.

    Args:
        token: The Google ID token to verify
        client_id: Optional Google OAuth client ID for verification

    Returns:
        dict: User information from the token (email, name, etc.)

    Raises:
        ValueError: If the token is invalid
    """
    try:
        # Verify the token
        # If client_id is provided, it will verify the audience matches
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), client_id)

        # Token is valid, return user info
        return {
            "email": idinfo.get("email"),
            "email_verified": idinfo.get("email_verified", False),
            "name": idinfo.get("name", ""),
            "given_name": idinfo.get("given_name", ""),
            "family_name": idinfo.get("family_name", ""),
            "picture": idinfo.get("picture", ""),
            "sub": idinfo.get("sub"),  # Google user ID
        }
    except ValueError as e:
        # Invalid token
        raise ValueError(f"Invalid Google token: {str(e)}")
