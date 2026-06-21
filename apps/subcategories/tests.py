"""Tests for subcategories app — subcategory CRUD endpoints."""

import uuid

import pytest
from rest_framework import status


@pytest.mark.django_db
class TestListSubcategoriesByUserCategory:
    def url(self, user_category_id):
        return f"/api/subcategories/{user_category_id}/sub-categories/"

    def test_returns_subcategory_with_no_transactions(
        self, auth_client, user_category, subcategory
    ):
        response = auth_client.get(self.url(user_category.id))
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == subcategory.name
        assert data[0]["transaction_type"] is None
        assert data[0]["amount"] is None

    def test_returns_one_row_per_transaction(
        self, auth_client, test_user, user_category, subcategory, transaction
    ):
        from datetime import date

        from apps.transactions.models import Transaction, TransactionType
        Transaction.objects.create(
            user_id=test_user.id,
            user_category=user_category,
            sub_category=subcategory,
            transaction_type=TransactionType.CREDIT,
            transaction_with="Employer",
            amount="3000.00",
            date=date.today(),
            created_by=test_user.id,
            updated_by=test_user.id,
        )
        response = auth_client.get(self.url(user_category.id))
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 2

    def test_unauthenticated_returns_401(self, api_client, user_category):
        response = api_client.get(self.url(user_category.id))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestCreateSubcategory:
    URL = "/api/subcategories/sub-category/"

    def test_create_subcategory_success(self, auth_client, user_category):
        response = auth_client.post(self.URL, {
            "name": "Coffee Shops",
            "user_category": str(user_category.id),
        })
        assert response.status_code == status.HTTP_201_CREATED

    def test_create_returns_list_for_user_category(self, auth_client, user_category, subcategory):
        response = auth_client.post(self.URL, {
            "name": "Restaurants",
            "user_category": str(user_category.id),
        })
        assert response.status_code == status.HTTP_201_CREATED
        names = [item["name"] for item in response.json()]
        assert "Restaurants" in names

    def test_create_missing_name_returns_400(self, auth_client, user_category):
        response = auth_client.post(self.URL, {"user_category": str(user_category.id)})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_unauthenticated_returns_401(self, api_client, user_category):
        response = api_client.post(self.URL, {
            "name": "Coffee Shops",
            "user_category": str(user_category.id),
        })
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestUpdateSubcategory:
    def url(self, pk):
        return f"/api/subcategories/sub-category/{pk}/"

    def test_update_subcategory_success(self, auth_client, subcategory):
        response = auth_client.post(self.url(subcategory.id), {"name": "Supermarket"})
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["name"] == "Supermarket"

    def test_update_nonexistent_returns_404(self, auth_client):
        response = auth_client.post(self.url(uuid.uuid4()), {"name": "X"})
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_unauthenticated_returns_401(self, api_client, subcategory):
        response = api_client.post(self.url(subcategory.id), {"name": "X"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestDeleteSubcategory:
    def url(self, pk):
        return f"/api/subcategories/delete-sub-category/{pk}/"

    def test_delete_soft_deletes_subcategory(self, auth_client, subcategory):
        response = auth_client.get(self.url(subcategory.id))
        assert response.status_code == status.HTTP_200_OK
        subcategory.refresh_from_db()
        assert subcategory.is_deleted is True

    def test_delete_nonexistent_returns_404(self, auth_client):
        response = auth_client.get(self.url(uuid.uuid4()))
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_unauthenticated_returns_401(self, api_client, subcategory):
        response = api_client.get(self.url(subcategory.id))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
