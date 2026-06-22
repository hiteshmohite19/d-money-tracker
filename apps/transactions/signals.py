from decimal import Decimal

from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.categories.models import CategoryTransactions
from apps.endusers.models import EndUser

from .models import Transaction, TransactionType


@receiver(post_save, sender=Transaction)
def update_category_transactions(sender, instance, created, **kwargs):
    """
    Update CategoryTransactions when a transaction is created.

    - DEBIT: Subtract amount (make negative)
    - CREDIT: Add amount (make positive)
    - EMI: Treat as DEBIT
    """
    if not created:
        return

    # Get or create CategoryTransactions record
    category_transaction, ct_created = CategoryTransactions.objects.get_or_create(
        user_id_id=instance.user_id,
        category_id=instance.user_category,
        defaults={"amount": Decimal("0.00")},
    )

    # Calculate amount change based on transaction type
    transaction_amount = Decimal(str(instance.amount))

    if instance.transaction_type == TransactionType.CREDIT:
        # Credit adds to amount
        category_transaction.amount += transaction_amount
    elif instance.transaction_type in [TransactionType.DEBIT, TransactionType.EMI]:
        # Debit and EMI subtract from amount (make negative)
        category_transaction.amount -= transaction_amount

    category_transaction.save()


@receiver(post_save, sender=Transaction)
def update_user_available_balance(sender, instance, created, **kwargs):
    """
    Update user's available_balance when a transaction is created.

    - CREDIT: Add to balance
    - DEBIT: Subtract from balance
    """
    if not created:
        return

    try:
        end_user = EndUser.objects.get(id=instance.user_id)
        if end_user.available_balance is not None:
            transaction_amount = Decimal(str(instance.amount))

            if instance.transaction_type == TransactionType.CREDIT:
                end_user.available_balance += transaction_amount
            elif instance.transaction_type == TransactionType.DEBIT:
                end_user.available_balance -= transaction_amount

            end_user.save(update_fields=["available_balance"])
    except EndUser.DoesNotExist:
        pass
