"""
Development settings.

Activate:
    export DJANGO_SETTINGS_MODULE=dmoneytracker.settings.development
    python manage.py runserver
"""

from .base import *  # noqa: F401, F403

# ---------------------------------------------------------------------------
# Override core
# ---------------------------------------------------------------------------
DEBUG = True
ALLOWED_HOSTS = ["*"]

# ---------------------------------------------------------------------------
# Logging  –  verbose console in dev
# ---------------------------------------------------------------------------
LOGGING["handlers"]["console"]["formatter"] = "verbose"  # noqa: F405
