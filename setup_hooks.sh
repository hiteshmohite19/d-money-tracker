#!/bin/bash
# Setup script for pre-commit hooks

echo "=== Setting up pre-commit hooks ==="

# Install dev dependencies
echo "Installing dev dependencies..."
pip install -e ".[dev]"

# Install pre-commit hooks
echo "Installing pre-commit hooks..."
pre-commit install

# Run pre-commit on all files to verify setup
echo "Running pre-commit checks on all files..."
pre-commit run --all-files

echo ""
echo "=== Setup complete! ==="
echo ""
echo "Pre-commit hooks are now active. They will run automatically before each commit."
echo ""
echo "Useful commands:"
echo "  - Run manually: pre-commit run --all-files"
echo "  - Run tests only: pytest"
echo "  - Format code: ruff format ."
echo "  - Lint code: ruff check . --fix"
echo "  - Skip hooks (not recommended): git commit --no-verify"
