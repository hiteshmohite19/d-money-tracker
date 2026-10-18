from datetime import date, timedelta
from decimal import Decimal

from celery import shared_task
from django.db.models import Sum

from apps.endusers.models import EndUser
from apps.transactions.models import Transaction, TransactionType

from .models import Report


@shared_task
def generate_report():
    yesterday = date.today() - timedelta(days=1)

    month = yesterday.month
    year = str(yesterday.year)
    day = yesterday.isoweekday()  # 1=Monday … 7=Sunday
    date_of_month = yesterday.day

    for user in EndUser.objects.filter(is_active=True):
        print(user)
        expense_total = (
            Transaction.objects.filter(
                user_id=user.id,
                date=yesterday,
                is_deleted=False,
                transaction_type__in=[TransactionType.DEBIT, TransactionType.EMI],
            ).aggregate(total=Sum("amount"))["total"]
            or Decimal("0")
        )

        budget = user.income or Decimal("0")

        Report.objects.update_or_create(
            user_id=user,
            month=month,
            year=year,
            defaults={
                "expense": expense_total,
                "budget": budget,
                "day": day,
                "date": date_of_month,
            },
        )
