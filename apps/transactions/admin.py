from django.contrib import admin

from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = [
        "date",
        "transaction_type",
        "amount",
        "transaction_with",
        "user_category",
        "sub_category",
        "is_active",
        "is_deleted",
    ]
    list_filter = [
        "transaction_type",
        "is_active",
        "is_deleted",
        "date",
        "created_at",
    ]
    search_fields = [
        "user_id",
        "transaction_with",
        "user_category__name",
        "sub_category__name",
    ]
    readonly_fields = [
        "id",
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
    ]
    date_hierarchy = "date"
    autocomplete_fields = ["user_category", "sub_category"]

    fieldsets = (
        (
            "Transaction Information",
            {
                "fields": (
                    "user_id",
                    "user_category",
                    "sub_category",
                    "transaction_type",
                    "transaction_with",
                    "amount",
                    "date",
                    "transaction_proof",
                ),
            },
        ),
        (
            "EMI Details",
            {
                "fields": (
                    "emi_frequency",
                    "emi_period",
                    "emi_amount",
                    "emi_start_date",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Status",
            {
                "fields": ("is_active", "is_deleted"),
            },
        ),
        (
            "Metadata",
            {
                "fields": (
                    "id",
                    "created_at",
                    "created_by",
                    "updated_at",
                    "updated_by",
                ),
                "classes": ("collapse",),
            },
        ),
    )

    def save_model(self, request, obj, form, change):
        """Save the model instance."""
        # Note: created_by and updated_by are UUID fields - set manually or via API
        super().save_model(request, obj, form, change)
