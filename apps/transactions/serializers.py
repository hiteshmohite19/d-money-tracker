from rest_framework import serializers

from .models import Transaction


class SubCategoryDetailSerializer(serializers.Serializer):
    """Nested serializer for subcategory details."""

    id = serializers.UUIDField(read_only=True)
    name = serializers.CharField(read_only=True)
    description = serializers.CharField(read_only=True, allow_null=True)


class TransactionSerializer(serializers.ModelSerializer):
    """Full serializer for Transaction model."""

    category = serializers.CharField(source="user_category.name", read_only=True)
    sub_category = SubCategoryDetailSerializer(read_only=True)
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, coerce_to_string=False)
    emi_amount = serializers.DecimalField(
        max_digits=12, decimal_places=2, coerce_to_string=False, required=False, allow_null=True
    )
    user_category_id = serializers.UUIDField(source="user_category.id", read_only=True)
    sub_category_id = serializers.UUIDField(source="sub_category.id", read_only=True)

    class Meta:
        model = Transaction
        fields = [
            "id",
            "user_id",
            "user_category_id",
            "category",
            "sub_category_id",
            "sub_category",
            "transaction_type",
            "transaction_with",
            "description",
            "amount",
            "date",
            "transaction_proof",
            "emi_frequency",
            "emi_period",
            "emi_amount",
            "emi_start_date",
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


class TransactionListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing transactions."""

    category = serializers.CharField(source="user_category.name", read_only=True)
    sub_category = serializers.CharField(source="sub_category.name", read_only=True)
    sub_category_description = serializers.CharField(
        source="sub_category.description", read_only=True, allow_null=True
    )
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, coerce_to_string=False)
    user_category_id = serializers.UUIDField(source="user_category.id", read_only=True)
    sub_category_id = serializers.UUIDField(source="sub_category.id", read_only=True)

    class Meta:
        model = Transaction
        fields = [
            "id",
            "user_category_id",
            "category",
            "sub_category_id",
            "sub_category",
            "sub_category_description",
            "transaction_type",
            "transaction_with",
            "description",
            "amount",
            "date",
            "is_active",
            "is_deleted",
        ]


class TransactionCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating transactions."""

    amount = serializers.DecimalField(max_digits=12, decimal_places=2, coerce_to_string=False)
    emi_amount = serializers.DecimalField(
        max_digits=12, decimal_places=2, coerce_to_string=False, required=False, allow_null=True
    )

    class Meta:
        model = Transaction
        fields = [
            "user_id",
            "user_category",
            "sub_category",
            "transaction_type",
            "transaction_with",
            "description",
            "amount",
            "date",
            "transaction_proof",
            "emi_frequency",
            "emi_period",
            "emi_amount",
            "emi_start_date",
            "is_active",
            "is_deleted",
        ]

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value

    def validate_date(self, value):
        from datetime import date
        if value > date.today():
            raise serializers.ValidationError("Transaction date cannot be in the future.")
        return value

    def validate_user_category(self, value):
        request = self.context.get("request")
        if request and value.user_id != request.user.id:
            raise serializers.ValidationError("Category does not belong to the authenticated user.")
        return value

    def validate_sub_category(self, value):
        request = self.context.get("request")
        if request and value.user_id != request.user.id:
            raise serializers.ValidationError("Sub-category does not belong to the authenticated user.")
        return value

    def validate(self, data):
        from .models import TransactionType

        transaction_type = data.get("transaction_type")

        if transaction_type == TransactionType.EMI:
            errors = {}
            if not data.get("emi_frequency"):
                errors["emi_frequency"] = "EMI frequency is required for EMI transactions"
            if not data.get("emi_period"):
                errors["emi_period"] = "EMI period is required for EMI transactions"
            if not data.get("emi_amount"):
                errors["emi_amount"] = "EMI amount is required for EMI transactions"
            if not data.get("emi_start_date"):
                errors["emi_start_date"] = "EMI start date is required for EMI transactions"

            if errors:
                raise serializers.ValidationError(errors)

        return data
