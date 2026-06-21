"""
Production settings.

Activate:
    export DJANGO_SETTINGS_MODULE=dmoneytracker.settings.production
    gunicorn dmoneytracker.wsgi:application
"""

from .base import *  # noqa: F401, F403

# ---------------------------------------------------------------------------
# Core
# ---------------------------------------------------------------------------
DEBUG = False

# ---------------------------------------------------------------------------
# Security headers & cookie flags
# ---------------------------------------------------------------------------
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

SECURE_SSL_REDIRECT = True

SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"

CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = "Lax"

# ---------------------------------------------------------------------------
# Whitenoise  –  compressed, cached static files
# ---------------------------------------------------------------------------
WHITENOISE_AUTOREFRESH = False
WHITENOISE_COMPRESS_NOSTREAM = True

# ---------------------------------------------------------------------------
# DRF  –  drop the browsable API renderer in production
# ---------------------------------------------------------------------------
REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = [  # noqa: F405
    "rest_framework.renderers.JSONRenderer",
]

# ---------------------------------------------------------------------------
# Logging  –  file handler set to WARNING in production
# ---------------------------------------------------------------------------
LOGGING["loggers"]["django"]["level"] = "WARNING"  # noqa: F405


SECRET_KEY = config("SECRET_KEY")  # required in production — no fallback
