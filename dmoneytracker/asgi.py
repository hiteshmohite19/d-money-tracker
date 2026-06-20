"""
ASGI entry-point  –  ready for future WebSocket / channels support.

Usage:
    uvicorn dmoneytracker.asgi:application --host 0.0.0.0 --port 8000
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dmoneytracker.settings.development")

application = get_asgi_application()
