from datetime import date

from django.db import transaction
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from apps.categories.models import Category

from .google_auth import verify_google_token
from .jwt_utils import decode_refresh_token, generate_token, generate_tokens
from .models import EndUser, UserCategories, UserMonthlyBudget
from .serializers import (
    EndUserListSerializer,
    EndUserSerializer,
    MobileSignInSerializer,
    UserCategoriesCreateUpdateSerializer,
    UserCategoriesListSerializer,
)


def _create_user_categories(user):
    """
    Private method to create user categories for a new user.

    Fetches all active categories from the Category table and creates
    corresponding entries in the UserCategories table for the given user.

    Args:
        user: EndUser instance
    """
    print("_create_user_categories ", user)
    # Get all active categories
    active_categories = Category.objects.filter(active=True)

    # Create UserCategories entries for each active category
    user_categories_to_create = []
    for category in active_categories:
        user_category = UserCategories(
            user_id=user.id,  # Pass UUID, not EndUser object
            name=category.name,
            created_by=user.id,
            updated_by=user.id,
        )
        user_categories_to_create.append(user_category)

    # Bulk create all user categories
    if user_categories_to_create:
        UserCategories.objects.bulk_create(user_categories_to_create)


def _sync_monthly_budget(user):
    today = date.today()
    income = str(user.income or "0")
    expense = str(user.estimated_expense or "0")

    last = (
        UserMonthlyBudget.objects.filter(user_id=user, active=True).order_by("-created_at").first()
    )

    if last and last.income == income and last.expense == expense:
        return

    UserMonthlyBudget.objects.filter(user_id=user).update(active=False)

    UserMonthlyBudget.objects.create(
        user_id=user,
        income=income,
        expense=expense,
        month=today.strftime("%B"),
        year=str(today.year),
        active=True,
    )


class EndUserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for EndUser model.

    Custom Endpoints:
    - POST /register/ - Register a new user (public)
    - POST /login/ - Login with mobile (public)
    - POST /update-user/ - Update authenticated user
    - POST /deactivate/ - Deactivate authenticated user
    """

    queryset = EndUser.objects.all()

    def get_permissions(self):
        public_actions = ["register", "login", "refresh_token", "verify_otp"]
        if self.action in public_actions:
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == "list":
            return EndUserListSerializer
        # if self.action in ["create", "update", "partial_update", "register", "update_user"]:
        #     return EndUserCreateUpdateSerializer
        return EndUserSerializer

    @action(detail=False, methods=["post"], url_path="register")
    def register(self, request):
        """POST /register/ - Register a new user and return JWT token."""
        with transaction.atomic():
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            user = serializer.instance

            # Create user categories from system categories
            _create_user_categories(user)
            _sync_monthly_budget(user)

        # Generate tokens (outside transaction as it's read-only)
        tokens = generate_tokens(user)

        # Get user categories
        user_categories = UserCategories.objects.filter(
            user_id=user.id,
            is_deleted=False,
        )
        categories_serializer = UserCategoriesListSerializer(user_categories, many=True)

        response_serializer = EndUserSerializer(user)
        return Response(
            {
                "user": response_serializer.data,
                "access_token": tokens["access_token"],
                "refresh_token": tokens["refresh_token"],
                "user_categories": categories_serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=["post"], url_path="login")
    def login(self, request):
        """POST /login/ - Login with mobile and return JWT token."""
        mobile = request.data.get("mobile")

        if not mobile:
            return Response(
                {"error": "mobile is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = EndUser.objects.get(mobile=mobile)
        except EndUser.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not user.is_active:
            return Response(
                {"error": "User account is deactivated"},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Generate access and refresh tokens
        tokens = generate_tokens(user)

        # Get user categories
        user_categories = UserCategories.objects.filter(
            user_id=user.id,
            is_deleted=False,
        )
        categories_serializer = UserCategoriesListSerializer(user_categories, many=True)

        response_serializer = EndUserSerializer(user)
        return Response(
            {
                "user": response_serializer.data,
                "access_token": tokens["access_token"],
                "refresh_token": tokens["refresh_token"],
                "user_categories": categories_serializer.data,
            },
            status=status.HTTP_200_OK,
        )

        # @action(detail=False, methods=["post"], url_path="signin")
        # def signin(self, request):
        """POST /signin/ - Sign in with Google token."""
        google_token = request.data.get("google_token")

        if not google_token:
            return Response(
                {"error": "google_token is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Verify Google token and extract user info
            user_info = verify_google_token(google_token)
        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Extract user details from Google token
        email = user_info.get("email")
        given_name = user_info.get("given_name", "")
        family_name = user_info.get("family_name", "")
        email_verified = user_info.get("email_verified", False)

        if not email:
            return Response(
                {"error": "Invalid email id"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if user exists by email
        try:
            user = EndUser.objects.get(email=email)
            # User exists, update verification status if needed
            if email_verified and not user.email_verified:
                user.email_verified = True
                user.save()
            created = False
        except EndUser.DoesNotExist:
            # Create new user from Google info using serializer
            user_data = {
                "first_name": given_name or "User",
                "last_name": family_name or "",
                "email": email,
                "email_verified": email_verified,
                "is_active": True,
            }

            serializer = EndUserCreateUpdateSerializer(data=user_data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            created = True

            # Create user categories from system categories
            _create_user_categories(user)

        # Generate access and refresh tokens
        tokens = generate_tokens(user)

        # Get user categories
        user_categories = UserCategories.objects.filter(
            user_id=user.id,
            is_deleted=False,
        )
        categories_serializer = UserCategoriesListSerializer(user_categories, many=True)

        response_serializer = EndUserSerializer(user)
        return Response(
            {
                "user": response_serializer.data,
                "access_token": tokens["access_token"],
                "refresh_token": tokens["refresh_token"],
                "created": created,
                "user_categories": categories_serializer.data,
            },
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )

    @action(detail=False, methods=["post"], url_path="update-user")
    def update_user(self, request):
        """POST /update-user/ - Update authenticated user."""
        user = request.user
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        _sync_monthly_budget(serializer.instance)

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

    @action(detail=False, methods=["post"], url_path="refresh-token")
    def refresh_token(self, request):
        """POST /refresh-token/ - Get new access token using refresh token."""
        refresh_token = request.data.get("refresh_token")

        if not refresh_token:
            return Response(
                {"error": "refresh_token is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Decode and validate refresh token
        payload = decode_refresh_token(refresh_token)
        if not payload:
            return Response(
                {"error": "Invalid or expired refresh token"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Get user from token
        try:
            user = EndUser.objects.get(id=payload["id"])
        except EndUser.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not user.is_active:
            return Response(
                {"error": "User account is deactivated"},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Generate new access token
        new_access_token = generate_token(user)

        return Response(
            {
                "access_token": new_access_token,
            },
            status=status.HTTP_200_OK,
        )

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

                # Create user categories from system categories
                _create_user_categories(user)

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
