from django.db import models

from apps.core.models import TimestampModel
from apps.endusers.models import UserCategories
from apps.subcategories.models import SubCategory


class TransactionType(models.TextChoices):
    """Transaction type choices."""

    CREDIT = "CREDIT", "Credit"
    DEBIT = "DEBIT", "Debit"
    EMI = "EMI", "EMI"


class EMIFrequency(models.TextChoices):
    """EMI frequency choices."""

    DAILY = "DAILY", "Daily"
    WEEKLY = "WEEKLY", "Weekly"
    MONTHLY = "MONTHLY", "Monthly"
    QUARTERLY = "QUARTERLY", "Quarterly"
    YEARLY = "YEARLY", "Yearly"


class Transaction(TimestampModel):
    """
    Transaction model for tracking financial transactions.

    Inherits id, created_at, updated_at from TimestampModel.
    Supports regular transactions (CREDIT/DEBIT) and EMI transactions.
    """

    # User reference
    user_id = models.UUIDField(help_text="User ID who owns this transaction", db_index=True)

    # Category references
    user_category = models.ForeignKey(
        UserCategories,
        on_delete=models.CASCADE,
        related_name="transactions",
        help_text="User category for this transaction",
    )
    sub_category = models.ForeignKey(
        SubCategory,
        on_delete=models.CASCADE,
        related_name="transactions",
        help_text="Sub-category for this transaction",
    )

    # Transaction details
    transaction_type = models.CharField(
        max_length=10,
        choices=TransactionType.choices,
        help_text="Type of transaction (CREDIT, DEBIT, or EMI)",
    )
    transaction_with = models.CharField(
        max_length=255,
        help_text="Person or entity involved in the transaction",
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Transaction amount",
    )
    date = models.DateField(
        help_text="Transaction date",
    )
    description = models.TextField(
        null=True,
        blank=True,
        help_text="Optional description for the transaction",
    )
    transaction_proof = models.FileField(
        upload_to="transaction_proofs/%Y/%m/%d/",
        null=True,
        blank=True,
        help_text="Optional proof document for the transaction",
    )

    # EMI-specific fields (only applicable when transaction_type is EMI)
    emi_frequency = models.CharField(
        max_length=20,
        choices=EMIFrequency.choices,
        null=True,
        blank=True,
        help_text="EMI payment frequency (only for EMI transactions)",
    )
    emi_period = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="EMI period in months (only for EMI transactions)",
    )
    emi_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="EMI installment amount (only for EMI transactions)",
    )
    emi_start_date = models.DateField(
        null=True,
        blank=True,
        help_text="EMI start date (only for EMI transactions)",
    )

    # Status flags
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this transaction is currently active",
    )
    is_deleted = models.BooleanField(
        default=False,
        help_text="Soft delete flag",
    )

    # Audit fields
    created_by = models.UUIDField(
        null=True,
        blank=True,
        help_text="User ID who created this transaction",
    )
    updated_by = models.UUIDField(
        null=True,
        blank=True,
        help_text="User ID who last updated this transaction",
    )

    class Meta:
        db_table = "transactions"
        verbose_name = "Transaction"
        verbose_name_plural = "Transactions"
        ordering = ["-date", "-created_at"]
        indexes = [
            models.Index(fields=["user_id"]),
            models.Index(fields=["user_id", "date"]),
            models.Index(fields=["user_category"]),
            models.Index(fields=["sub_category"]),
            models.Index(fields=["transaction_type"]),
            models.Index(fields=["is_active"]),
            models.Index(fields=["is_deleted"]),
        ]

    def __str__(self):
        return f"{self.transaction_type} - {self.amount} - {self.date}"

    def __repr__(self):
        return f"<Transaction: {self.transaction_type} {self.amount} on {self.date}>"

    def clean(self):
        """Validate that EMI fields are provided when transaction_type is EMI."""
        from django.core.exceptions import ValidationError

        if self.transaction_type == TransactionType.EMI:
            errors = {}
            if not self.emi_frequency:
                errors["emi_frequency"] = "EMI frequency is required for EMI transactions"
            if not self.emi_period:
                errors["emi_period"] = "EMI period is required for EMI transactions"
            if not self.emi_amount:
                errors["emi_amount"] = "EMI amount is required for EMI transactions"
            if not self.emi_start_date:
                errors["emi_start_date"] = "EMI start date is required for EMI transactions"

            if errors:
                raise ValidationError(errors)
