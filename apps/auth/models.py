from django.db import models

from apps.core.constants import AccountTypeEnum
from apps.core.models import TimestampModel


class AccountType(TimestampModel):
    account_type = models.CharField(
        max_length=20,
        choices=AccountTypeEnum.choices,
        unique=True,
    )
    status = models.BooleanField(default=True)

    class Meta:
        db_table = "account_types"
        verbose_name = "Account Type"
        verbose_name_plural = "Account Types"

    def __str__(self):
        return self.account_type
