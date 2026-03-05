from rest_framework import serializers

from .models import Category


class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for Category model.
    """

    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "active",
            "last_update_by",
            "last_update_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "last_update_at"]


class CategoryListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing categories.
    """

    class Meta:
        model = Category
        fields = ["id", "name", "active"]
