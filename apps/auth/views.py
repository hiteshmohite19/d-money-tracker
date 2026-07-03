from django.db import transaction
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.endusers.google_auth import verify_google_token
from apps.endusers.jwt_utils import decode_refresh_token, generate_token, generate_tokens
from apps.endusers.models import EndUser, UserCategories
from apps.endusers.serializers import EndUserSerializer, UserCategoriesListSerializer
from apps.endusers.utils import create_user_categories, sync_monthly_budget


class AuthViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    @action(detail=False, methods=["post"], url_path="register")
    def register(self, request):
        with transaction.atomic():
            serializer = EndUserSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            user = serializer.instance
            create_user_categories(user)
            sync_monthly_budget(user)

        tokens = generate_tokens(user)
        user_categories = UserCategories.objects.filter(user_id=user.id, is_deleted=False)
        return Response(
            {
                "user": EndUserSerializer(user).data,
                "access_token": tokens["access_token"],
                "refresh_token": tokens["refresh_token"],
                "user_categories": UserCategoriesListSerializer(user_categories, many=True).data,
            },
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=["post"], url_path="login")
    def login(self, request):
        mobile = request.data.get("mobile")
        if not mobile:
            return Response({"error": "mobile is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = EndUser.objects.get(mobile=mobile)
        except EndUser.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        if not user.is_active:
            return Response(
                {"error": "User account is deactivated"}, status=status.HTTP_403_FORBIDDEN
            )

        tokens = generate_tokens(user)
        user_categories = UserCategories.objects.filter(user_id=user.id, is_deleted=False)
        return Response(
            {
                "user": EndUserSerializer(user).data,
                "access_token": tokens["access_token"],
                "refresh_token": tokens["refresh_token"],
                "user_categories": UserCategoriesListSerializer(user_categories, many=True).data,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["post"], url_path="signin")
    def signin(self, request):
        google_token = request.data.get("access_token")
        print(request.data)
        if not google_token:
            return Response(
                {"error": "google_token is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user_info = verify_google_token(google_token)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        email = user_info.get("email")
        if not email:
            return Response({"error": "Invalid email id"}, status=status.HTTP_400_BAD_REQUEST)

        given_name = user_info.get("given_name", "")
        family_name = user_info.get("family_name", "")
        email_verified = user_info.get("email_verified", False)

        try:
            user = EndUser.objects.get(email=email)
            if email_verified and not user.email_verified:
                user.email_verified = True
                user.save()
            created = False
        except EndUser.DoesNotExist:
            serializer = EndUserSerializer(
                data={
                    "first_name": given_name or "User",
                    "last_name": family_name or "",
                    "email": email,
                    "email_verified": email_verified,
                    "is_active": True,
                }
            )
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            create_user_categories(user)
            created = True

        tokens = generate_tokens(user)
        user_categories = UserCategories.objects.filter(user_id=user.id, is_deleted=False)
        return Response(
            {
                "user": EndUserSerializer(user).data,
                "access_token": tokens["access_token"],
                "refresh_token": tokens["refresh_token"],
                "created": created,
                "user_categories": UserCategoriesListSerializer(user_categories, many=True).data,
            },
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )

    @action(detail=False, methods=["post"], url_path="refresh-token")
    def refresh_token(self, request):
        refresh_token = request.data.get("refresh_token")
        if not refresh_token:
            return Response(
                {"error": "refresh_token is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        payload = decode_refresh_token(refresh_token)
        if not payload:
            return Response(
                {"error": "Invalid or expired refresh token"}, status=status.HTTP_401_UNAUTHORIZED
            )

        try:
            user = EndUser.objects.get(id=payload["id"])
        except EndUser.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        if not user.is_active:
            return Response(
                {"error": "User account is deactivated"}, status=status.HTTP_403_FORBIDDEN
            )

        return Response({"access_token": generate_token(user)}, status=status.HTTP_200_OK)
