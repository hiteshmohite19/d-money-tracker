from django.db import transaction
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .jwt_utils import generate_tokens
from .models import EndUser, UserCategories
from .serializers import (
    EndUserListSerializer,
    EndUserSerializer,
    MobileSignInSerializer,
    UserCategoriesCreateUpdateSerializer,
    UserCategoriesListSerializer,
)
from .utils import create_user_categories, sync_monthly_budget


class EndUserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for EndUser model.

    Custom Endpoints:
    - POST /update-user/ - Update authenticated user
    - POST /deactivate/ - Deactivate authenticated user
    - GET /profile/ - Get authenticated user details
    - POST /verify-otp/ - Verify OTP
    """

    queryset = EndUser.objects.all()

    def get_permissions(self):
        if self.action == "verify_otp":
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == "list":
            return EndUserListSerializer
        return EndUserSerializer

    @action(detail=False, methods=["post"], url_path="update-user")
    def update_user(self, request):
        """POST /update-user/ - Update authenticated user."""
        user = request.user
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        sync_monthly_budget(serializer.instance)

        response_serializer = EndUserSerializer(serializer.instance)
        return Response(response_serializer.data)

    @action(detail=False, methods=["post"], url_path="deactivate")
    def deactivate(self, request):
        """POST /deactivate/ - Deactivate authenticated user."""
        user = request.user
        user.is_active = False
        user.save()

        return Response(
            {"message": "User account deactivated successfully"},
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["get"], url_path="profile")
    def get_user(self, request):
        """GET /profile/ - Get authenticated user details."""
        user = request.user
        serializer = EndUserSerializer(user)
        return Response(serializer.data)

    @action(detail=False, methods=["post"], url_path="verify-otp")
    def verify_otp(self, request):
        """
        POST /verify-otp/ - Verify OTP and create user or return verification message.

        Request body:
        {
            "mobile": "+918956047638",
            "otp": "111111"
        }

        If OTP matches and user doesn't exist: creates user and returns JWT tokens
        If OTP matches and user exists: returns mobile verified message
        If OTP doesn't match: returns error
        """
        mobile = request.data.get("mobile")
        otp = request.data.get("otp")

        # Validate required fields
        if not mobile:
            return Response(
                {"error": "Mobile number is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not otp:
            return Response(
                {"error": "OTP is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Verify OTP (hardcoded for now)
        VALID_OTP = "111111"
        if otp != VALID_OTP:
            return Response(
                {"error": "Invalid OTP"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = None
        # Check if user exists
        try:
            user = EndUser.objects.get(mobile=mobile)
            # User exists, return verification message

        except EndUser.DoesNotExist:
            # User doesn't exist, create new user in a transaction
            with transaction.atomic():
                user_data = {
                    "mobile": mobile,
                }

                serializer = MobileSignInSerializer(data=user_data)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                user = serializer.instance

                create_user_categories(user)

            # Generate tokens (outside transaction as it's read-only)
        tokens = generate_tokens(user)

        # Get user categories
        user_categories = UserCategories.objects.filter(
            user_id=user.id,
            is_deleted=False,
        )
        categories_serializer = UserCategoriesListSerializer(user_categories, many=True)

        # Return user data with tokens
        response_serializer = EndUserSerializer(user)
        return Response(
            {
                "message": "User created successfully",
                "user": response_serializer.data,
                "access_token": tokens["access_token"],
                "refresh_token": tokens["refresh_token"],
                "user_categories": categories_serializer.data,
                "user_exists": False,
            },
            status=status.HTTP_201_CREATED,
        )


class UserCategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for UserCategories (requires JWT authentication).

    Endpoints:
    - GET /user-categories/ - List user categories
    - POST /category/ - Create new user category
    - POST /update-categories/<id>/ - Update user category
    - GET /delete-category/?id=<id> - Soft delete user category
    """

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return user categories for authenticated user, excluding soft deleted."""
        return UserCategories.objects.filter(
            user_id=self.request.user.id,
            is_deleted=False,
        )

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update", "update_category"]:
            return UserCategoriesCreateUpdateSerializer
        return UserCategoriesListSerializer

    def list(self, request, *args, **kwargs):
        """GET /user-categories/ - List all user categories for authenticated user."""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """
        POST /category/ - Create a new user category.

        Returns all user categories for the user after creation.
        """
        user = request.user
        data = request.data.copy()
        data["user_id"] = str(user.id)

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save(created_by=user.id)

        # Return all user categories for the user
        all_categories = self.get_queryset()
        response_serializer = UserCategoriesListSerializer(all_categories, many=True)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="update")
    def update_category(self, request, pk=None):
        """POST /update-categories/<id>/ - Update a user category."""
        user = request.user
        instance = self.get_object()
        data = request.data.copy()
        data["user_id"] = str(user.id)

        serializer = self.get_serializer(instance, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=user.id)

        response_serializer = UserCategoriesListSerializer(serializer.instance)
        return Response(response_serializer.data)

    @action(detail=False, methods=["get"], url_path="delete")
    def delete_category(self, request):
        """GET /delete-category/?id=<id> - Soft delete a user category."""
        user = request.user
        category_id = request.query_params.get("id")

        if not category_id:
            return Response(
                {"error": "id query parameter is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            instance = UserCategories.objects.get(
                id=category_id,
                user_id=user.id,
                is_deleted=False,
            )
        except UserCategories.DoesNotExist:
            return Response(
                {"error": "User category not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        instance.is_deleted = True
        instance.updated_by = user.id
        instance.save()

        return Response(
            {"message": "User category deleted successfully"},
            status=status.HTTP_200_OK,
        )
