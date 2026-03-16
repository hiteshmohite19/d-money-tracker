from django.contrib import admin

from .models import Wishlist


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ["item", "user_id", "price", "date", "is_deleted", "created_at"]
    list_filter = ["is_deleted", "date", "created_at"]
    search_fields = ["item", "user_id__first_name", "user_id__last_name", "description"]
    readonly_fields = ["id", "created_at", "updated_at", "created_by", "updated_by"]
    date_hierarchy = "date"

    fieldsets = (
        (
            "Wishlist Item Information",
            {
                "fields": ("user_id", "item", "price", "description", "date"),
            },
        ),
        (
            "Status",
            {
                "fields": ("is_deleted",),
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
