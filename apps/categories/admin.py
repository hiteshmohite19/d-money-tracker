from django.contrib import admin

from .models import Category, CategoryTransactions


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "active", "last_update_by", "last_update_at", "created_at"]
    list_filter = ["active", "created_at", "last_update_at"]
    search_fields = ["name"]
    readonly_fields = ["id", "created_at", "updated_at", "last_update_at"]
    date_hierarchy = "created_at"

    fieldsets = (
        (
            "Basic Information",
            {
                "fields": ("name", "active"),
            },
        ),
        (
            "Metadata",
            {
                "fields": ("id", "last_update_by", "last_update_at", "created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    def save_model(self, request, obj, form, change):
        """Save the model instance."""
        # Note: last_update_by is a UUID field - set manually or via API
        super().save_model(request, obj, form, change)


@admin.register(CategoryTransactions)
class CategoryTransactionsAdmin(admin.ModelAdmin):
    list_display = ["user_id", "category_id", "amount", "created_at", "updated_at"]
    list_filter = ["created_at", "updated_at"]
    search_fields = ["user_id__first_name", "user_id__last_name", "category_id__name"]
    readonly_fields = ["id", "created_at", "updated_at"]
    date_hierarchy = "created_at"
    autocomplete_fields = ["user_id", "category_id"]

    fieldsets = (
        (
            "Transaction Summary",
            {
                "fields": ("user_id", "category_id", "amount"),
            },
        ),
        (
            "Metadata",
            {
                "fields": ("id", "created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )
