from django.db import models

from app.apps.core.models import TimestampModel
from app.apps.endusers.models import EndUser, UserCategories


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


class CategoryTransactions(TimestampModel):
    """
    Track cumulative transaction amounts per user and category.

    Amount represents the running total:
    - DEBIT transactions subtract (negative)
    - CREDIT transactions add (positive)

    Updated automatically via signals when transactions are created.
    """

    user_id = models.ForeignKey(
        EndUser,
        on_delete=models.CASCADE,
        related_name="category_transactions",
        help_text="User who owns these transactions",
    )
    category_id = models.ForeignKey(
        UserCategories,
        on_delete=models.CASCADE,
        related_name="category_transactions",
        help_text="Category for these transactions",
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="Cumulative amount (negative for debits, positive for credits)",
    )

    class Meta:
        db_table = "category_transactions"
        verbose_name = "Category Transaction Summary"
        verbose_name_plural = "Category Transaction Summaries"
        ordering = ["-created_at"]
        unique_together = [["user_id", "category_id"]]
        indexes = [
            models.Index(fields=["user_id"]),
            models.Index(fields=["category_id"]),
            models.Index(fields=["user_id", "category_id"]),
        ]

    def __str__(self):
        return f"{self.user_id.full_name} - {self.category_id.name}: {self.amount}"
