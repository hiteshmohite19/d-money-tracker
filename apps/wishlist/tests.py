"""Tests for wishlist app — wishlist CRUD endpoints."""

import uuid

import pytest
from rest_framework import status

from apps.wishlist.models import Wishlist


@pytest.fixture
def wishlist_item(db, test_user):
    return Wishlist.objects.create(
        user_id=test_user,
        item="MacBook Pro",
        price="150000.00",
        description="Latest M3 chip",
        expected_date="2026-12-01",
        created_by=test_user.id,
        updated_by=test_user.id,
    )


@pytest.mark.django_db
class TestListWishlist:
    URL = "/api/wishlist/"

    def test_list_returns_user_items(self, auth_client, wishlist_item):
        response = auth_client.get(self.URL)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 1

    def test_list_excludes_soft_deleted(self, auth_client, wishlist_item):
        wishlist_item.is_deleted = True
        wishlist_item.save()
        response = auth_client.get(self.URL)
        assert len(response.json()) == 0

    def test_list_excludes_other_users_items(self, auth_client, second_user, db):
        Wishlist.objects.create(
            user_id=second_user,
            item="iPhone",
            price="80000.00",
            expected_date="2026-12-01",
            created_by=second_user.id,
            updated_by=second_user.id,
        )
        response = auth_client.get(self.URL)
        assert len(response.json()) == 0

    def test_list_unauthenticated_returns_401(self, api_client):
        response = api_client.get(self.URL)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestCreateWishlistItem:
    URL = "/api/wishlist/create/"

    def test_create_item_success(self, auth_client):
        response = auth_client.post(self.URL, {
            "item": "AirPods Pro",
            "price": "25000.00",
            "expected_date": "2026-12-01",
        })
        assert response.status_code == status.HTTP_200_OK

    def test_create_returns_full_list(self, auth_client, wishlist_item):
        response = auth_client.post(self.URL, {
            "item": "iPad",
            "price": "60000.00",
            "expected_date": "2026-12-01",
        })
        items = [i["item"] for i in response.json()]
        assert "MacBook Pro" in items
        assert "iPad" in items

    def test_create_with_optional_fields(self, auth_client):
        response = auth_client.post(self.URL, {
            "item": "Gaming Chair",
            "price": "15000.00",
            "description": "Ergonomic office chair",
            "expected_date": "2026-09-01",
        })
        assert response.status_code == status.HTTP_200_OK

    def test_create_missing_item_returns_400(self, auth_client):
        response = auth_client.post(self.URL, {"price": "1000.00"})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_unauthenticated_returns_401(self, api_client):
        response = api_client.post(self.URL, {"item": "X", "price": "100.00"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestUpdateWishlistItem:
    def url(self, pk):
        return f"/api/wishlist/{pk}/update/"

    def test_update_item_success(self, auth_client, wishlist_item):
        response = auth_client.post(self.url(wishlist_item.id), {"price": "140000.00"})
        assert response.status_code == status.HTTP_200_OK

    def test_update_returns_full_list(self, auth_client, wishlist_item):
        response = auth_client.post(self.url(wishlist_item.id), {"item": "MacBook Air"})
        assert response.status_code == status.HTTP_200_OK
        items = [i["item"] for i in response.json()]
        assert "MacBook Air" in items

    def test_update_unauthenticated_returns_401(self, api_client, wishlist_item):
        response = api_client.post(self.url(wishlist_item.id), {"price": "1.00"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestDeleteWishlistItem:
    URL = "/api/wishlist/delete/"

    def test_delete_soft_deletes_item(self, auth_client, wishlist_item):
        response = auth_client.get(self.URL, {"id": str(wishlist_item.id)})
        assert response.status_code == status.HTTP_200_OK
        wishlist_item.refresh_from_db()
        assert wishlist_item.is_deleted is True

    def test_delete_returns_remaining_list(self, auth_client, wishlist_item, db, test_user):
        Wishlist.objects.create(
            user_id=test_user,
            item="Keyboard",
            price="5000.00",
            expected_date="2026-12-01",
            created_by=test_user.id,
            updated_by=test_user.id,
        )
        response = auth_client.get(self.URL, {"id": str(wishlist_item.id)})
        items = [i["item"] for i in response.json()]
        assert "MacBook Pro" not in items
        assert "Keyboard" in items

    def test_delete_missing_id_returns_400(self, auth_client):
        response = auth_client.get(self.URL)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_delete_nonexistent_id_returns_404(self, auth_client):
        response = auth_client.get(self.URL, {"id": str(uuid.uuid4())})
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_unauthenticated_returns_401(self, api_client, wishlist_item):
        response = api_client.get(self.URL, {"id": str(wishlist_item.id)})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
