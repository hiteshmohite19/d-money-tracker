"""Tests for categories app — category-transactions endpoint."""

from decimal import Decimal

import pytest
from rest_framework import status

from apps.categories.models import CategoryTransactions


@pytest.mark.django_db
class TestCategoryTransactions:
    URL = "/api/categories/category-transactions/"

    def test_returns_all_user_categories(self, auth_client, user_category):
        response = auth_client.get(self.URL)
        assert response.status_code == status.HTTP_200_OK
        ids = [str(item["category_id"]) for item in response.json()]
        assert str(user_category.id) in ids

    def test_category_with_no_transactions_returns_zero(self, auth_client, user_category):
        response = auth_client.get(self.URL)
        data = response.json()
        entry = next(i for i in data if str(i["category_id"]) == str(user_category.id))
        assert Decimal(str(entry["amount"])) == Decimal("0.00")

    def test_category_with_debit_transaction_returns_negative_amount(
        self, auth_client, test_user, user_category
    ):
        CategoryTransactions.objects.create(
            user_id=test_user,
            category_id=user_category,
            amount=Decimal("-150.00"),
        )
        response = auth_client.get(self.URL)
        data = response.json()
        entry = next(i for i in data if str(i["category_id"]) == str(user_category.id))
        assert Decimal(str(entry["amount"])) == Decimal("-150.00")

    def test_category_with_credit_transaction_returns_positive_amount(
        self, auth_client, test_user, user_category
    ):
        CategoryTransactions.objects.create(
            user_id=test_user,
            category_id=user_category,
            amount=Decimal("5000.00"),
        )
        response = auth_client.get(self.URL)
        data = response.json()
        entry = next(i for i in data if str(i["category_id"]) == str(user_category.id))
        assert Decimal(str(entry["amount"])) == Decimal("5000.00")

    def test_excludes_other_users_categories(self, auth_client, second_user, db):
        from apps.endusers.models import UserCategories
        other_cat = UserCategories.objects.create(
            user_id=second_user.id,
            name="Other User Category",
            created_by=second_user.id,
            updated_by=second_user.id,
        )
        response = auth_client.get(self.URL)
        ids = [str(item["category_id"]) for item in response.json()]
        assert str(other_cat.id) not in ids

    def test_unauthenticated_returns_401(self, api_client):
        response = api_client.get(self.URL)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
