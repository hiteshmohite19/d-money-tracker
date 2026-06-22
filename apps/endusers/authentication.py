from rest_framework import authentication, exceptions

from .jwt_utils import get_user_from_token


class JWTAuthentication(authentication.BaseAuthentication):
    """
    Custom JWT authentication for EndUser.

    Expects header: Authorization: Bearer <token>
    """

    keyword = "Bearer"

    def authenticate(self, request):
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return None

        parts = auth_header.split()

        if len(parts) != 2 or parts[0] != self.keyword:
            return None

        token = parts[1]
        user = get_user_from_token(token)

        if not user:
            raise exceptions.AuthenticationFailed("Invalid or expired token")

        if not user.is_active:
            raise exceptions.AuthenticationFailed("User account is deactivated")

        return (user, token)

    def authenticate_header(self, request):
        return self.keyword
