from django.db import models

from apps.core.constants import DayEnum, MonthEnum
from apps.core.models import TimestampModel
from apps.endusers.models import EndUser


class Report(TimestampModel):
    user_id = models.ForeignKey(
        EndUser,
        on_delete=models.CASCADE,
        related_name="reports",
    )
    month = models.IntegerField(choices=MonthEnum.choices)
    year = models.CharField(max_length=10)
    day = models.IntegerField(choices=DayEnum.choices, null=True, blank=True)
    date = models.IntegerField(null=True, blank=True)
    budget = models.DecimalField(max_digits=12, decimal_places=2)
    expense = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        db_table = "reports"
        verbose_name = "Report"
        verbose_name_plural = "Reports"
        ordering = ["-year", "-month"]
        constraints = [
            models.UniqueConstraint(
                fields=["user_id", "month", "year"],
                name="unique_report_per_user_month_year",
            )
        ]

    def __str__(self):
        return f"{self.user_id_id} - {MonthEnum(self.month).label} {self.year}"
