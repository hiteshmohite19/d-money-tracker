from django.apps import AppConfig


class EndusersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.endusers"
    verbose_name = "End Users"

    def ready(self):
        """Import signal handlers when Django starts."""
        import app.apps.endusers.signals  # noqa: F401
