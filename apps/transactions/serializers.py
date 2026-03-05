from rest_framework import serializers

from .models import Transaction


class TransactionSerializer(serializers.ModelSerializer):
    """Full serializer for Transaction model."""

    user_category_name = serializers.CharField(source="user_category.name", read_only=True)
    sub_category_name = serializers.CharField(source="sub_category.name", read_only=True)

    class Meta:
        model = Transaction
        fields = [
            "id",
            "user_id",
            "user_category",
            "user_category_name",
            "sub_category",
            "sub_category_name",
            "transaction_type",
            "transaction_with",
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

    user_category_name = serializers.CharField(source="user_category.name", read_only=True)
    sub_category_name = serializers.CharField(source="sub_category.name", read_only=True)

    class Meta:
        model = Transaction
        fields = [
            "id",
            "user_category",
            "user_category_name",
            "sub_category",
            "sub_category_name",
            "transaction_type",
            "transaction_with",
            "amount",
            "date",
            "is_active",
            "is_deleted",
        ]


class TransactionCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating transactions."""

    class Meta:
        model = Transaction
        fields = [
            "user_id",
            "user_category",
            "sub_category",
            "transaction_type",
            "transaction_with",
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

    def validate(self, data):
        """Validate that EMI fields are provided when transaction_type is EMI."""
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
