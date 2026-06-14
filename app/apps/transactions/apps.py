from django.apps import AppConfig


class TransactionsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.transactions"

    def ready(self):
        """Import signals when app is ready."""
        import app.apps.transactions.signals  # noqa: F401
