from django.core.validators import EmailValidator, RegexValidator
from django.db import models

from apps.core.models import TimestampModel


class EndUser(TimestampModel):
    """
    End User model representing app users/customers.

    Inherits id, created_at, updated_at from TimestampModel.
    """

    # Personal Information
    first_name = models.CharField(
        max_length=100,
        help_text="User's first name",
    )
    last_name = models.CharField(
        max_length=100,
        help_text="User's last name",
    )
    email = models.EmailField(
        max_length=255,
        unique=True,
        validators=[EmailValidator()],
        help_text="User's email address",
    )

    # Contact - mobile is unique
    mobile = models.CharField(
        max_length=20,
        validators=[
            RegexValidator(
                regex=r"^\+?1?\d{9,15}$",
                message="Mobile number must be entered in the format: '+999999999'. Up to 15 digits allowed.",
            )
        ],
        help_text="User's mobile number (unique)",
    )

    # Status flags
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this user account is currently active",
    )
    mobile_verified = models.BooleanField(
        default=False,
        help_text="Whether the mobile number has been verified",
    )
    email_verified = models.BooleanField(
        default=False,
        help_text="Whether the email address has been verified",
    )

    # Financial Information
    income = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="User's monthly income",
    )
    estimated_expense = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="User's estimated monthly expenses",
    )
    expected_saving = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="User's expected monthly savings",
    )
    available_balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Available balance for the current month (auto-updated)",
    )

    # Audit fields
    created_by = models.UUIDField(
        null=True,
        blank=True,
        help_text="User ID who created this end user",
    )
    updated_by = models.UUIDField(
        null=True,
        blank=True,
        help_text="User ID who last updated this end user",
    )

    class Meta:
        db_table = "endusers"
        verbose_name = "End User"
        verbose_name_plural = "End Users"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["mobile"]),
            models.Index(fields=["email"]),
            models.Index(fields=["is_active"]),
            models.Index(fields=["mobile_verified"]),
            models.Index(fields=["email_verified"]),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.mobile})"

    def __repr__(self):
        return f"<EndUser: {self.first_name} {self.last_name} - {self.mobile}>"

    def save(self, *args, **kwargs):
        """Override save to auto-update available_balance."""
        # On creation or when estimated_expense changes, update available_balance
        if self.pk is None:
            # New user - set available_balance to estimated_expense
            self.available_balance = self.estimated_expense
        else:
            # Existing user - check if estimated_expense changed
            try:
                old_instance = EndUser.objects.get(pk=self.pk)
                if old_instance.estimated_expense != self.estimated_expense:
                    # estimated_expense changed, update available_balance
                    self.available_balance = self.estimated_expense
            except EndUser.DoesNotExist:
                # Instance doesn't exist yet, set available_balance
                self.available_balance = self.estimated_expense

        super().save(*args, **kwargs)

    @property
    def full_name(self):
        """Return the user's full name."""
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def verification_status(self):
        """Return verification status summary."""
        return {
            "mobile": self.mobile_verified,
            "email": self.email_verified,
            "fully_verified": self.mobile_verified and self.email_verified,
        }

    @property
    def is_authenticated(self):
        """Always return True for authenticated EndUser instances."""
        return True

    @property
    def is_anonymous(self):
        """Always return False for EndUser instances."""
        return False


class UserCategories(TimestampModel):
    """
    User-specific categories for organizing transactions.
    Each user can create their own custom categories.
    """

    user_id = models.UUIDField(
        help_text="User ID who owns this category",
    )
    name = models.CharField(
        max_length=100,
        help_text="Category name",
    )

    # Status flags
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this user category is currently active",
    )
    is_deleted = models.BooleanField(
        default=False,
        help_text="Soft delete flag",
    )

    # Audit fields
    created_by = models.UUIDField(
        null=True,
        blank=True,
        help_text="User ID who created this user category",
    )
    updated_by = models.UUIDField(
        null=True,
        blank=True,
        help_text="User ID who last updated this user category",
    )

    class Meta:
        db_table = "user_categories"
        verbose_name = "User Category"
        verbose_name_plural = "User Categories"
        ordering = ["user_id", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["user_id", "name"],
                name="unique_user_category_per_user",
            )
        ]
        indexes = [
            models.Index(fields=["user_id"]),
            models.Index(fields=["is_active"]),
            models.Index(fields=["is_deleted"]),
        ]

    def __str__(self):
        return f"User {self.user_id} - {self.name}"

    def __repr__(self):
        return f"<UserCategories: {self.user_id} - {self.name}>"


class UserMonthlyBudget(TimestampModel):
    user_id = models.ForeignKey(
        EndUser,
        on_delete=models.CASCADE,
        related_name="monthly_budgets",
    )
    income = models.CharField(max_length=255)
    expense = models.CharField(max_length=255)
    month = models.CharField(max_length=20)
    year = models.CharField(max_length=10)
    active = models.BooleanField(default=True)

    class Meta:
        db_table = "user_monthly_budget"
