from django.db import models

from apps.core.models import TimestampModel


class Category(TimestampModel):
    """
    Category model for organizing transactions.

    Inherits id, created_at, updated_at from TimestampModel.
    """

    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Category name (must be unique)",
    )
    active = models.BooleanField(
        default=True,
        help_text="Whether this category is currently active",
    )
    last_update_by = models.UUIDField(
        null=True,
        blank=True,
        help_text="User ID who last updated this category",
    )
    last_update_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp of the last update",
    )

    class Meta:
        db_table = "categories"
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["active"]),
            models.Index(fields=["name"]),
        ]

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<Category: {self.name} (active={self.active})>"
