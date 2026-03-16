from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Wishlist
from .serializers import (
    WishlistCreateUpdateSerializer,
    WishlistListSerializer,
    WishlistSerializer,
)


class WishlistViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Wishlist model (requires JWT authentication).

    Endpoints:
    - GET /wishlist/ - List user's wishlist items
    - POST /wishlist/ - Create new wishlist item
    - POST /wishlist/<id>/update/ - Update wishlist item
    - GET /wishlist/delete/?id=<id> - Soft delete wishlist item
    """

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return wishlist items for authenticated user, excluding soft deleted."""
        return Wishlist.objects.filter(
            user_id=self.request.user.id,
            is_deleted=False,
        )

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update", "update_item"]:
            return WishlistCreateUpdateSerializer
        if self.action == "list":
            return WishlistListSerializer
        return WishlistSerializer

    def list(self, request, *args, **kwargs):
        """GET /wishlist/ - List all wishlist items for authenticated user."""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """POST /wishlist/ - Create a new wishlist item."""
        user = request.user
        data = request.data.copy()
        data["user_id"] = str(user.id)

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save(created_by=user.id)

        response_serializer = WishlistListSerializer(serializer.instance)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="update")
    def update_item(self, request, pk=None):
        """POST /wishlist/<id>/update/ - Update a wishlist item."""
        user = request.user
        instance = self.get_object()
        data = request.data.copy()
        data["user_id"] = str(user.id)

        serializer = self.get_serializer(instance, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=user.id)

        response_serializer = WishlistListSerializer(serializer.instance)
        return Response(response_serializer.data)

    @action(detail=False, methods=["get"], url_path="delete")
    def delete_item(self, request):
        """GET /wishlist/delete/?id=<id> - Soft delete a wishlist item."""
        user = request.user
        item_id = request.query_params.get("id")

        if not item_id:
            return Response(
                {"error": "id query parameter is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            instance = Wishlist.objects.get(
                id=item_id,
                user_id=user.id,
                is_deleted=False,
            )
        except Wishlist.DoesNotExist:
            return Response(
                {"error": "Wishlist item not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        instance.is_deleted = True
        instance.updated_by = user.id
        instance.save()

        return Response(
            {"message": "Wishlist item deleted successfully"},
            status=status.HTTP_200_OK,
        )
