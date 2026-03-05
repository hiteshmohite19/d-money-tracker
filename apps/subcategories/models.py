from django.db import models

from apps.core.models import TimestampModel
from apps.endusers.models import UserCategories


class SubCategory(TimestampModel):
    """
    SubCategory model for fine-grained transaction categorization.

    Inherits id, created_at, updated_at from TimestampModel.
    Links to UserCategories and stores user_id for ownership.
    """

    name = models.CharField(
        max_length=100,
        help_text="Subcategory name",
    )

    # Reference IDs
    user_id = models.UUIDField(
        help_text="User ID who owns this subcategory",
    )
    user_category = models.ForeignKey(
        UserCategories,
        on_delete=models.CASCADE,
        related_name="subcategories",
        help_text="Parent user category",
    )

    # Status flags
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this subcategory is currently active",
    )
    is_deleted = models.BooleanField(
        default=False,
        help_text="Soft delete flag",
    )

    # Audit fields
    created_by = models.UUIDField(
        null=True,
        blank=True,
        help_text="User ID who created this subcategory",
    )
    updated_by = models.UUIDField(
        null=True,
        blank=True,
        help_text="User ID who last updated this subcategory",
    )

    class Meta:
        db_table = "sub_categories"
        verbose_name = "Subcategory"
        verbose_name_plural = "Subcategories"
        ordering = ["user_category", "name"]
        indexes = [
            models.Index(fields=["user_id", "user_category"]),
            models.Index(fields=["is_active"]),
            models.Index(fields=["is_deleted"]),
        ]
        # Ensure unique subcategory names per user per user_category
        constraints = [
            models.UniqueConstraint(
                fields=["user_id", "user_category", "name"],
                name="unique_subcategory_per_user_category",
            )
        ]

    def __str__(self):
        return f"{self.name}"

    def __repr__(self):
        return f"<SubCategory: {self.name} (user={self.user_id})>"
