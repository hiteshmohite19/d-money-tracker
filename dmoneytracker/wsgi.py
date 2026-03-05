"""
WSGI entry-point  –  used by gunicorn in production.

Usage:
    gunicorn dmoneytracker.wsgi:application
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dmoneytracker.settings.development")

application = get_wsgi_application()
