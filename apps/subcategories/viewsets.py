from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import SubCategory
from .serializers import (
    SubCategoryCreateUpdateSerializer,
    SubCategoryListSerializer,
    SubCategorySerializer,
)


class SubCategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for SubCategory model (requires JWT authentication).

    Custom Endpoints:
    - GET /{user_category_id}/sub-categories/ - List subcategories for user and user_category
    - POST /sub-category/ - Create new subcategory
    - POST /sub-category/{id}/ - Update subcategory
    - GET /delete-sub-category/{id}/ - Soft delete subcategory
    """

    queryset = SubCategory.objects.filter(is_deleted=False)
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "list":
            return SubCategoryListSerializer
        if self.action in [
            "create",
            "update",
            "partial_update",
            "create_sub_category",
            "update_sub_category",
        ]:
            return SubCategoryCreateUpdateSerializer
        return SubCategorySerializer

    def get_queryset(self):
        """Return subcategories for authenticated user, excluding soft deleted."""
        return SubCategory.objects.filter(
            user_id=self.request.user.id,
            is_deleted=False,
        ).select_related("user_category")

    def list_by_user_category(self, request, user_category_id=None):
        """GET /{user_category_id}/sub-categories/ - List subcategories for user and user_category."""
        queryset = self.get_queryset().filter(user_category_id=user_category_id)
        serializer = SubCategoryListSerializer(queryset, many=True)
        return Response(serializer.data)

    def create_sub_category(self, request):
        """POST /sub-category/ - Create a new subcategory."""
        user = request.user
        data = request.data.copy()
        data["user_id"] = str(user.id)

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save(created_by=user.id)

        response_serializer = SubCategoryListSerializer(serializer.instance)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    def update_sub_category(self, request, pk=None):
        """POST /sub-category/{id}/ - Update a subcategory."""
        user = request.user
        try:
            instance = SubCategory.objects.get(
                id=pk,
                user_id=user.id,
                is_deleted=False,
            )
        except SubCategory.DoesNotExist:
            return Response(
                {"error": "Subcategory not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        data = request.data.copy()
        data["user_id"] = str(user.id)

        serializer = self.get_serializer(instance, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=user.id)

        response_serializer = SubCategoryListSerializer(serializer.instance)
        return Response(response_serializer.data)

    def delete_sub_category(self, request, pk=None):
        """GET /delete-sub-category/{id}/ - Soft delete a subcategory."""
        user = request.user
        try:
            instance = SubCategory.objects.get(
                id=pk,
                user_id=user.id,
                is_deleted=False,
            )
        except SubCategory.DoesNotExist:
            return Response(
                {"error": "Subcategory not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        instance.is_deleted = True
        instance.updated_by = user.id
        instance.save()

        return Response(
            {"message": "Subcategory deleted successfully"},
            status=status.HTTP_200_OK,
        )
