from rest_framework import serializers

from .models import Wishlist


class WishlistSerializer(serializers.ModelSerializer):
    """Serializer for Wishlist model."""

    class Meta:
        model = Wishlist
        fields = [
            "id",
            "user_id",
            "item",
            "price",
            "description",
            "date",
            "is_deleted",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
        ]


class WishlistListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing wishlist items."""

    class Meta:
        model = Wishlist
        fields = [
            "id",
            "user_id",
            "item",
            "price",
            "description",
            "date",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class WishlistCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating wishlist items."""

    class Meta:
        model = Wishlist
        fields = [
            "user_id",
            "item",
            "price",
            "description",
            "date",
        ]

    def validate_price(self, value):
        """Ensure price is positive."""
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than zero.")
        return value
