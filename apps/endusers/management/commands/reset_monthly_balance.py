from django.core.management.base import BaseCommand
from django.db.models import F

from apps.endusers.models import EndUser


class Command(BaseCommand):
    help = 'Reset available_balance to estimated_expense for all users at the start of each month'

    def handle(self, *args, **options):
        # Update all active users' available_balance to match their estimated_expense
        updated_count = EndUser.objects.filter(
            is_active=True,
            estimated_expense__isnull=False
        ).update(available_balance=F('estimated_expense'))

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully reset available_balance for {updated_count} users'
            )
        )
