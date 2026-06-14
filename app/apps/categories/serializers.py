from rest_framework import serializers

from .models import Category, CategoryTransactions


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


class CategoryTransactionsSerializer(serializers.ModelSerializer):
    """
    Serializer for CategoryTransactions model.
    Returns amount as absolute value (always positive).
    """

    amount = serializers.SerializerMethodField()
    category_name = serializers.CharField(source="category_id.name", read_only=True)
    user_name = serializers.CharField(source="user_id.full_name", read_only=True)

    class Meta:
        model = CategoryTransactions
        fields = [
            "id",
            "user_id",
            "user_name",
            "category_id",
            "category_name",
            "amount",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_amount(self, obj):
        """Return absolute value of amount (always positive)."""
        return abs(obj.amount)


class CategoryTransactionsRawSerializer(serializers.ModelSerializer):
    """
    Serializer for CategoryTransactions model.
    Returns amount as-is (negative for debits, positive for credits).
    """

    class Meta:
        model = CategoryTransactions
        fields = [
            "category_id",
            "amount",
        ]
        read_only_fields = ["category_id", "amount"]
