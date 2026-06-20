from django.contrib import admin

from .models import EndUser, UserCategories


@admin.register(EndUser)
class EndUserAdmin(admin.ModelAdmin):
    list_display = [
        "full_name",
        "mobile",
        "email",
        "is_active",
        "mobile_verified",
        "email_verified",
        "created_at",
    ]
    list_filter = [
        "is_active",
        "mobile_verified",
        "email_verified",
        "created_at",
        "updated_at",
    ]
    search_fields = ["first_name", "last_name", "email", "mobile"]
    readonly_fields = [
        "id",
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
    ]
    date_hierarchy = "created_at"

    fieldsets = (
        (
            "Personal Information",
            {
                "fields": ("first_name", "last_name", "email", "mobile"),
            },
        ),
        (
            "Status & Verification",
            {
                "fields": ("is_active", "mobile_verified", "email_verified"),
            },
        ),
        (
            "Financial Information",
            {
                "fields": ("income", "estimated_expense", "expected_saving"),
                "classes": ("collapse",),
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

    def full_name(self, obj):
        """Display full name in list view."""
        return obj.full_name

    full_name.short_description = "Full Name"
    full_name.admin_order_field = "first_name"


@admin.register(UserCategories)
class UserCategoriesAdmin(admin.ModelAdmin):
    list_display = ["user_id", "name", "is_active", "is_deleted", "created_at"]
    list_filter = ["is_active", "is_deleted", "created_at"]
    search_fields = ["user_id", "name"]
    readonly_fields = ["id", "created_at", "updated_at", "created_by", "updated_by"]
    date_hierarchy = "created_at"

    fieldsets = (
        (
            "Category Information",
            {
                "fields": ("user_id", "name"),
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
                "fields": ("id", "created_at", "created_by", "updated_at", "updated_by"),
                "classes": ("collapse",),
            },
        ),
    )
