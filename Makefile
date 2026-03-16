.PHONY: help install test lint format check clean hooks

help:  ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install all dependencies including dev dependencies
	pip install -e ".[dev]"

hooks:  ## Install pre-push hooks
	pre-commit install --hook-type pre-push
	@echo "Pre-push hooks installed successfully!"

test:  ## Run all tests
	pytest

test-cov:  ## Run tests with coverage report
	pytest --cov=apps --cov-report=html --cov-report=term-missing

lint:  ## Run linter (Ruff)
	ruff check .

lint-fix:  ## Run linter with auto-fix
	ruff check . --fix

format:  ## Format code using Ruff
	ruff format .

format-check:  ## Check if code is formatted correctly
	ruff format --check .

check:  ## Run Django system checks
	python manage.py check

migrations:  ## Check for missing migrations
	python manage.py makemigrations --check --dry-run

migrate:  ## Run migrations
	python manage.py migrate

pre-push:  ## Run all pre-push hooks manually
	pre-commit run --all-files --hook-stage push

clean:  ## Clean up Python cache files
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name '*.pyc' -delete
	find . -type f -name '*.pyo' -delete
	find . -type d -name '*.egg-info' -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache htmlcov .coverage

setup:  ## Complete setup: install dependencies and hooks
	$(MAKE) install
	$(MAKE) hooks
	@echo ""
	@echo "Setup complete! Pre-push hooks are now active."

dev:  ## Run development server
	python manage.py runserver

shell:  ## Open Django shell
	python manage.py shell
