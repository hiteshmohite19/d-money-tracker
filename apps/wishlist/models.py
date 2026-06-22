from django.db import models

from apps.core.models import TimestampModel
from apps.endusers.models import EndUser


class Wishlist(TimestampModel):
    """
    Wishlist model for tracking user's desired items.

    Fields:
    - user_id: Reference to EndUser
    - item: Name of the wishlist item
    - price: Price of the item
    - description: Description of the item
    - date: Target date or date added
    - is_deleted: Soft delete flag
    """

    user_id = models.ForeignKey(
        EndUser,
        on_delete=models.CASCADE,
        related_name="wishlists",
        help_text="User who owns this wishlist item",
    )
    item = models.CharField(
        max_length=255,
        help_text="Name of the wishlist item",
    )
    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Price of the item",
    )
    description = models.TextField(
        blank=True,
        help_text="Description of the item",
    )
    expected_date = models.DateField(
        help_text="Target date or date added to wishlist",
    )
    is_deleted = models.BooleanField(
        default=False,
        help_text="Soft delete flag",
    )

    # Audit fields
    created_by = models.UUIDField(
        null=True,
        blank=True,
        help_text="User ID who created this wishlist item",
    )
    updated_by = models.UUIDField(
        null=True,
        blank=True,
        help_text="User ID who last updated this wishlist item",
    )

    class Meta:
        db_table = "wishlist"
        ordering = ["-expected_date", "-created_at"]
        verbose_name = "Wishlist Item"
        verbose_name_plural = "Wishlist Items"

    def __str__(self):
        return f"{self.item} - {self.user_id.full_name}"
