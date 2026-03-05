"""
pytest configuration for Django tests.
This file is automatically discovered by pytest.
"""
import os
import django
from django.conf import settings

# Configure Django settings before importing any Django models
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dmoneytracker.settings.dev')

def pytest_configure():
    """Configure Django for pytest."""
    django.setup()
