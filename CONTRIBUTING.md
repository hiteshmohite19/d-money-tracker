# Contributing to DMoneyTracker

## Development Setup

### Prerequisites
- Python 3.12+
- PostgreSQL
- pip

### Initial Setup

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd dmoneytracker
   ```

2. **Install dependencies and setup pre-push hooks:**
   ```bash
   make setup
   ```

   Or manually:
   ```bash
   pip install -e ".[dev]"
   pre-commit install --hook-type pre-push
   ```

3. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

4. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

5. **Create superuser:**
   ```bash
   python manage.py createsuperuser
   ```

## Development Workflow

### Pre-push Hooks

This project uses **pre-push hooks** to ensure code quality. Every push to remote will automatically:

1. ✅ **Format code** using Ruff
2. ✅ **Lint code** and fix issues
3. ✅ **Run Django system checks**
4. ✅ **Check for missing migrations**
5. ✅ **Run unit tests** (all tests must pass)
6. ✅ **Check for common issues** (trailing whitespace, large files, etc.)

**Important:** Pushes will be **blocked** if:
- Tests fail
- Code is not properly formatted
- Linting errors exist
- Django checks fail

### Running Tests

```bash
# Run all tests
make test

# Run tests with coverage
make test-cov

# Run specific test file
pytest apps/endusers/tests.py

# Run specific test
pytest apps/endusers/tests.py::TestEndUserModel::test_create_enduser
```

### Code Formatting

```bash
# Format all code
make format

# Check if code is formatted (without changing)
make format-check

# Lint and auto-fix issues
make lint-fix
```

### Manual Pre-push Check

```bash
# Run all pre-push hooks manually
make pre-push

# Or directly
pre-commit run --all-files --hook-stage push
```

### Common Commands

```bash
make help          # Show all available commands
make dev           # Run development server
make shell         # Open Django shell
make check         # Run Django system checks
make migrations    # Check for missing migrations
make migrate       # Run migrations
make clean         # Clean up cache files
```

## Code Quality Standards

### Formatting
- **Line length:** 100 characters max
- **Quote style:** Double quotes
- **Indent style:** 4 spaces
- **Formatter:** Ruff (automatic via pre-commit)

### Linting
- **Linter:** Ruff
- **Rules:** pycodestyle + pyflakes + isort
- **Auto-fix:** Enabled in pre-commit hooks

### Testing
- **Framework:** pytest
- **Coverage:** Minimum 0% (configure as needed)
- **All tests must pass before push**

## Bypassing Pre-push (Not Recommended)

In rare cases, you may need to bypass pre-push hooks:

```bash
git push --no-verify
```

⚠️ **Warning:** Only use this in exceptional circumstances. The CI/CD pipeline will still enforce all checks.

## Writing Tests

### Test Structure

```python
import pytest
from apps.your_app.models import YourModel

@pytest.mark.django_db
class TestYourModel:
    """Tests for YourModel."""
    
    def test_model_creation(self):
        """Test creating a model instance."""
        instance = YourModel.objects.create(
            field1="value1",
            field2="value2",
        )
        assert instance.field1 == "value1"
```

### Test Location
- Place tests in `apps/<app_name>/tests.py` or `apps/<app_name>/tests/`
- Use descriptive test names: `test_<what_is_being_tested>`

## Pull Request Process

1. Create a feature branch from `main`
2. Make your changes
3. Commit your changes locally (no pre-commit checks)
4. Push your branch (pre-push hooks will run automatically)
5. Create a pull request
6. Wait for code review and CI checks

## Questions?

If you have questions about the development workflow or pre-push hooks setup, please create an issue.
