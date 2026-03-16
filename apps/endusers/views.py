from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .google_auth import verify_google_token
from .jwt_utils import generate_token
from .models import EndUser, UserCategories
from .serializers import (
    EndUserCreateUpdateSerializer,
    EndUserListSerializer,
    EndUserSerializer,
    UserCategoriesCreateUpdateSerializer,
    UserCategoriesListSerializer,
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
        if self.action in ["register", "login"]:
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == "list":
            return EndUserListSerializer
        if self.action in ["create", "update", "partial_update", "register", "update_user"]:
            return EndUserCreateUpdateSerializer
        return EndUserSerializer

    # @action(detail=False, methods=["post"], url_path="register")
    # def register(self, request):
    #     """POST /register/ - Register a new user and return JWT token."""
    #     serializer = self.get_serializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save()

    #     user = serializer.instance
    #     token = generate_token(user)

    #     response_serializer = EndUserSerializer(user)
    #     return Response(
    #         {
    #             "user": response_serializer.data,
    #             "token": token,
    #         },
    #         status=status.HTTP_201_CREATED,
    #     )

    # @action(detail=False, methods=["post"], url_path="login")
    # def login(self, request):
    #     """POST /login/ - Login with mobile and return JWT token."""
    #     mobile = request.data.get("mobile")

    #     if not mobile:
    #         return Response(
    #             {"error": "mobile is required"},
    #             status=status.HTTP_400_BAD_REQUEST,
    #         )

    #     try:
    #         user = EndUser.objects.get(mobile=mobile)
    #     except EndUser.DoesNotExist:
    #         return Response(
    #             {"error": "User not found"},
    #             status=status.HTTP_404_NOT_FOUND,
    #         )

    #     if not user.is_active:
    #         return Response(
    #             {"error": "User account is deactivated"},
    #             status=status.HTTP_403_FORBIDDEN,
    #         )

    #     token = generate_token(user)

    #     response_serializer = EndUserSerializer(user)
    #     return Response(
    #         {
    #             "user": response_serializer.data,
    #             "token": token,
    #         },
    #         status=status.HTTP_200_OK,
    #     )

    @action(detail=False, methods=["post"], url_path="signin")
    def signin(self, request):
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

        # Generate JWT token
        token = generate_token(user)

        response_serializer = EndUserSerializer(user)
        return Response(
            {
                "user": response_serializer.data,
                "token": token,
                "created": created,
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

    @action(detail=False, methods=["get"], url_path="get-user")
    def get_user(self, request):
        """GET /get-user/ - Get authenticated user details."""
        user = request.user
        serializer = EndUserSerializer(user)
        return Response(serializer.data)


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
        """POST /category/ - Create a new user category."""
        user = request.user
        data = request.data.copy()
        data["user_id"] = str(user.id)

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save(created_by=user.id)

        response_serializer = UserCategoriesListSerializer(serializer.instance)
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
