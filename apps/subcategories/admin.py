from django.contrib import admin

from .models import SubCategory


@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "user_category",
        "user_id",
        "is_active",
        "is_deleted",
        "created_at",
    ]
    list_filter = [
        "is_active",
        "is_deleted",
        "user_category",
        "created_at",
        "updated_at",
    ]
    search_fields = ["name", "user_category__name", "user_id"]
    readonly_fields = [
        "id",
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
    ]
    date_hierarchy = "created_at"
    autocomplete_fields = ["user_category"]

    fieldsets = (
        (
            "Basic Information",
            {
                "fields": ("name", "user_category", "user_id"),
            },
        ),
        (
            "Status",
            {
                "fields": ("is_active", "is_deleted"),
            },
        ),
        (
            "Audit Information",
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
