from django.contrib import admin

from .models import Report


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ("user_id", "month", "year", "day", "date", "budget", "expense", "created_at")
    list_filter = ("month", "year", "day")
    search_fields = ("user_id__email", "year")
    ordering = ("-year", "-month")
    readonly_fields = ("created_at", "updated_at")
