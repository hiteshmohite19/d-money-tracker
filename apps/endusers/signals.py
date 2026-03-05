from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.endusers.models import EndUser


@receiver(post_save, sender=EndUser)
def create_user_categories(sender, instance, created, **kwargs):
    """
    Signal handler for EndUser creation.

    Users can create their own custom categories via the API,
    so no auto-population is needed.
    """
    if created:
        # Users will create their own categories via API
        pass
