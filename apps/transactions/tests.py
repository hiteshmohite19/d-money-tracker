"""Tests for transactions app — transaction CRUD endpoints."""

import uuid
from datetime import date

import pytest
from rest_framework import status

from apps.transactions.models import Transaction, TransactionType


@pytest.mark.django_db
class TestListTransactions:
    URL = "/api/transactions/transactions/"

    def test_list_returns_user_transactions(self, auth_client, transaction):
        response = auth_client.get(self.URL)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 1

    def test_list_excludes_soft_deleted(self, auth_client, transaction):
        transaction.is_deleted = True
        transaction.save()
        response = auth_client.get(self.URL)
        assert len(response.json()) == 0

    def test_list_excludes_other_users_transactions(
        self, auth_client, second_user, user_category, subcategory
    ):
        Transaction.objects.create(
            user_id=second_user.id,
            user_category=user_category,
            sub_category=subcategory,
            transaction_type=TransactionType.DEBIT,
            transaction_with="Other",
            amount="50.00",
            date=date.today(),
            created_by=second_user.id,
            updated_by=second_user.id,
        )
        response = auth_client.get(self.URL)
        assert len(response.json()) == 0

    def test_list_unauthenticated_returns_401(self, api_client):
        response = api_client.get(self.URL)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_response_fields(self, auth_client, transaction):
        data = auth_client.get(self.URL).json()
        item = data[0]
        assert "id" in item
        assert "category" in item
        assert "sub_category" in item
        assert "transaction_type" in item
        assert "amount" in item
        assert "date" in item


@pytest.mark.django_db
class TestCreateTransaction:
    URL = "/api/transactions/transaction/"

    def test_create_debit_transaction(self, auth_client, user_category, subcategory):
        response = auth_client.post(
            self.URL,
            {
                "user_category": str(user_category.id),
                "sub_category": str(subcategory.id),
                "transaction_type": "DEBIT",
                "transaction_with": "Amazon",
                "amount": "299.99",
                "date": str(date.today()),
            },
        )
        assert response.status_code == status.HTTP_201_CREATED

    def test_create_credit_transaction(self, auth_client, user_category, subcategory):
        response = auth_client.post(
            self.URL,
            {
                "user_category": str(user_category.id),
                "sub_category": str(subcategory.id),
                "transaction_type": "CREDIT",
                "transaction_with": "Employer",
                "amount": "5000.00",
                "date": str(date.today()),
            },
        )
        assert response.status_code == status.HTTP_201_CREATED

    def test_create_returns_full_list(self, auth_client, user_category, subcategory, transaction):
        auth_client.post(
            self.URL,
            {
                "user_category": str(user_category.id),
                "sub_category": str(subcategory.id),
                "transaction_type": "DEBIT",
                "transaction_with": "Netflix",
                "amount": "15.99",
                "date": str(date.today()),
            },
        )
        response = auth_client.post(
            self.URL,
            {
                "user_category": str(user_category.id),
                "sub_category": str(subcategory.id),
                "transaction_type": "DEBIT",
                "transaction_with": "Spotify",
                "amount": "9.99",
                "date": str(date.today()),
            },
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert len(response.json()) >= 3

    def test_create_missing_required_fields_returns_400(self, auth_client):
        response = auth_client.post(self.URL, {})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_amount_returned_as_number(self, auth_client, user_category, subcategory):
        response = auth_client.post(
            self.URL,
            {
                "user_category": str(user_category.id),
                "sub_category": str(subcategory.id),
                "transaction_type": "DEBIT",
                "transaction_with": "Shop",
                "amount": "49.99",
                "date": str(date.today()),
            },
        )
        amount = response.json()[0]["amount"]
        assert isinstance(amount, (int, float))

    def test_create_unauthenticated_returns_401(self, api_client):
        response = api_client.post(self.URL, {})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestUpdateTransaction:
    def url(self, pk):
        return f"/api/transactions/transaction/{pk}/"

    def test_update_transaction_success(self, auth_client, transaction):
        response = auth_client.post(self.url(transaction.id), {"transaction_with": "Costco"})
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["transaction_with"] == "Costco"

    def test_update_amount(self, auth_client, transaction):
        response = auth_client.post(self.url(transaction.id), {"amount": "200.00"})
        assert response.status_code == status.HTTP_200_OK

    def test_update_nonexistent_returns_404(self, auth_client):
        response = auth_client.post(self.url(uuid.uuid4()), {"transaction_with": "X"})
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_unauthenticated_returns_401(self, api_client, transaction):
        response = api_client.post(self.url(transaction.id), {"transaction_with": "X"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestDeleteTransaction:
    def url(self, pk):
        return f"/api/transactions/delete-transaction/{pk}/"

    def test_delete_soft_deletes_transaction(self, auth_client, transaction):
        response = auth_client.get(self.url(transaction.id))
        assert response.status_code == status.HTTP_200_OK
        transaction.refresh_from_db()
        assert transaction.is_deleted is True

    def test_deleted_transaction_excluded_from_list(self, auth_client, transaction):
        auth_client.get(self.url(transaction.id))
        response = auth_client.get("/api/transactions/transactions/")
        assert len(response.json()) == 0

    def test_delete_nonexistent_returns_404(self, auth_client):
        response = auth_client.get(self.url(uuid.uuid4()))
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_unauthenticated_returns_401(self, api_client, transaction):
        response = api_client.get(self.url(transaction.id))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
