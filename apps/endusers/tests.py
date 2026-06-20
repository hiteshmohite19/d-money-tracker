"""
Tests for the endusers app.
"""
import pytest
from django.contrib.auth import get_user_model
from app.apps.endusers.models import EndUser


@pytest.mark.django_db
class TestEndUserModel:
    """Tests for the EndUser model."""

    def test_create_enduser(self):
        """Test creating an EndUser instance."""
        user = EndUser.objects.create(
            first_name="Test",
            last_name="User",
            email="test@example.com",
            mobile="+1234567890",
            estimated_expense=10000,
        )
        assert user.first_name == "Test"
        assert user.last_name == "User"
        assert user.full_name == "Test User"
        assert user.available_balance == user.estimated_expense

    def test_enduser_string_representation(self):
        """Test the string representation of EndUser."""
        user = EndUser.objects.create(
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            mobile="+9876543210",
        )
        assert str(user) == "John Doe (+9876543210)"

    def test_available_balance_updates_with_estimated_expense(self):
        """Test that available_balance updates when estimated_expense changes."""
        user = EndUser.objects.create(
            first_name="Test",
            last_name="User",
            email="test@example.com",
            mobile="+1234567890",
            estimated_expense=10000,
        )
        assert user.available_balance == 10000

        # Update estimated_expense
        user.estimated_expense = 15000
        user.save()
        user.refresh_from_db()
        assert user.available_balance == 15000
