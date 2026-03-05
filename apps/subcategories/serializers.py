from rest_framework import serializers

from .models import SubCategory


class SubCategorySerializer(serializers.ModelSerializer):
    """
    Full serializer for SubCategory model.
    """

    user_category_name = serializers.CharField(source="user_category.name", read_only=True)

    class Meta:
        model = SubCategory
        fields = [
            "id",
            "name",
            "user_id",
            "user_category",
            "user_category_name",
            "is_active",
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


class SubCategoryListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing subcategories.
    """

    user_category_name = serializers.CharField(source="user_category.name", read_only=True)

    class Meta:
        model = SubCategory
        fields = [
            "id",
            "name",
            "user_category",
            "user_category_name",
            "is_active",
            "is_deleted",
        ]


class SubCategoryCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating/updating subcategories.
    Excludes audit fields which are set automatically.
    """

    class Meta:
        model = SubCategory
        fields = [
            "name",
            "user_id",
            "user_category",
            "is_active",
            "is_deleted",
        ]

    def validate(self, data):
        """Ensure unique subcategory name per user per user_category."""
        instance = self.instance
        user_id = data.get("user_id")
        user_category = data.get("user_category")
        name = data.get("name")

        # Build the query
        queryset = SubCategory.objects.filter(
            user_id=user_id,
            user_category=user_category,
            name=name,
        )

        # Exclude current instance when updating
        if instance:
            queryset = queryset.exclude(pk=instance.pk)

        if queryset.exists():
            raise serializers.ValidationError(
                "A subcategory with this name already exists for this user and category."
            )

        return data
