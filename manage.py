#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""

import os
import sys


def main() -> None:
    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dmoneytracker.settings.development")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you on the correct PYTHON_PATH extension? "
            "Try running this from the top-level project directory."
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
