from rest_framework import serializers

from .models import EndUser, UserCategories


class EndUserSerializer(serializers.ModelSerializer):
    """
    Full serializer for EndUser model.
    """

    full_name = serializers.CharField(read_only=True)
    verification_status = serializers.ReadOnlyField()

    class Meta:
        model = EndUser
        fields = [
            "id",
            "first_name",
            "last_name",
            "full_name",
            "email",
            "mobile",
            "is_active",
            "mobile_verified",
            "email_verified",
            "verification_status",
            "income",
            "estimated_expense",
            "available_balance",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
        ]
        read_only_fields = [
            "id",
            "available_balance",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
        ]


class EndUserListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing end users.
    """

    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = EndUser
        fields = [
            "id",
            "full_name",
            "mobile",
            "email",
            "is_active",
            "mobile_verified",
            "email_verified",
        ]


class MobileSignInSerializer(serializers.ModelSerializer):
    """
    Serializer for creating/updating end users.
    Excludes audit fields which are set automatically.
    """

    class Meta:
        model = EndUser
        fields = [
            "mobile",
        ]



class UserCategoriesSerializer(serializers.ModelSerializer):
    """Serializer for UserCategories model."""

    class Meta:
        model = UserCategories
        fields = [
            "id",
            "user_id",
            "name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


# ============================================================================
# UserCategories Serializers (for nested endpoints)
# ============================================================================


class UserCategoriesListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing user categories."""

    class Meta:
        model = UserCategories
        fields = [
            "id",
            "user_id",
            "name",
            "is_active",
            "is_deleted",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class UserCategoriesDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer with nested subcategories."""

    subcategories = serializers.SerializerMethodField()

    class Meta:
        model = UserCategories
        fields = [
            "id",
            "user_id",
            "name",
            "is_active",
            "is_deleted",
            "subcategories",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "created_by", "updated_by"]

    def get_subcategories(self, obj):
        """Fetch subcategories for this user category."""
        from apps.subcategories.models import SubCategory
        from apps.subcategories.serializers import SubCategoryListSerializer

        queryset = SubCategory.objects.filter(
            user_id=obj.user_id,
            user_category_id=obj.id,
        )

        include_deleted = self.context.get("include_deleted", False)
        if not include_deleted:
            queryset = queryset.filter(is_deleted=False)

        return SubCategoryListSerializer(queryset, many=True).data


class UserCategoriesCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating user categories."""

    class Meta:
        model = UserCategories
        fields = ["user_id", "name", "is_active", "is_deleted"]

    def validate(self, data):
        """Ensure unique category name per user."""
        instance = self.instance
        user_id = data.get("user_id")
        name = data.get("name")

        queryset = UserCategories.objects.filter(user_id=user_id, name=name)
        if instance:
            queryset = queryset.exclude(pk=instance.pk)

        if queryset.exists():
            raise serializers.ValidationError(
                "A category with this name already exists for this user."
            )
        return data


class EndUserDetailWithCategoriesSerializer(serializers.ModelSerializer):
    """EndUser serializer with nested user_categories and subcategories."""

    full_name = serializers.CharField(read_only=True)
    verification_status = serializers.ReadOnlyField()
    user_categories = serializers.SerializerMethodField()

    class Meta:
        model = EndUser
        fields = [
            "id",
            "first_name",
            "last_name",
            "full_name",
            "email",
            "mobile",
            "is_active",
            "mobile_verified",
            "email_verified",
            "verification_status",
            "income",
            "estimated_expense",
            "user_categories",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "created_by", "updated_by"]

    def get_user_categories(self, obj):
        """Fetch user categories with nested subcategories."""
        queryset = UserCategories.objects.filter(user_id=obj.id)

        include_deleted = self.context.get("include_deleted", False)
        if not include_deleted:
            queryset = queryset.filter(is_deleted=False)

        return UserCategoriesDetailSerializer(queryset, many=True, context=self.context).data
