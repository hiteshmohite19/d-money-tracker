"""Shared pytest fixtures for all app tests."""

import pytest
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def test_user(db):
    from apps.endusers.models import EndUser
    return EndUser.objects.create(
        first_name="Test",
        last_name="User",
        email="testuser@example.com",
        mobile="+919876543210",
    )


@pytest.fixture
def second_user(db):
    from apps.endusers.models import EndUser
    return EndUser.objects.create(
        first_name="Other",
        last_name="User",
        email="otheruser@example.com",
        mobile="+919876543211",
    )


@pytest.fixture
def auth_client(api_client, test_user):
    from apps.endusers.jwt_utils import generate_token
    token = generate_token(test_user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return api_client


@pytest.fixture
def system_category(db):
    from apps.categories.models import Category
    return Category.objects.create(name="Food & Dining", active=True)


@pytest.fixture
def user_category(test_user, system_category):
    from apps.endusers.models import UserCategories
    return UserCategories.objects.create(
        user_id=test_user.id,
        name=system_category.name,
        created_by=test_user.id,
        updated_by=test_user.id,
    )


@pytest.fixture
def subcategory(db, test_user, user_category):
    from apps.subcategories.models import SubCategory
    return SubCategory.objects.create(
        user_id=test_user.id,
        user_category=user_category,
        name="Groceries",
        created_by=test_user.id,
        updated_by=test_user.id,
    )


@pytest.fixture
def transaction(db, test_user, user_category, subcategory):
    from datetime import date

    from apps.transactions.models import Transaction, TransactionType
    return Transaction.objects.create(
        user_id=test_user.id,
        user_category=user_category,
        sub_category=subcategory,
        transaction_type=TransactionType.DEBIT,
        transaction_with="Walmart",
        amount="150.00",
        date=date.today(),
        created_by=test_user.id,
        updated_by=test_user.id,
    )
