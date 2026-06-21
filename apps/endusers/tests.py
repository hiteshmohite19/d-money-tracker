"""Tests for endusers app — auth, profile, and user category endpoints."""

import uuid
import pytest
from rest_framework import status

from apps.categories.models import Category
from apps.endusers.jwt_utils import generate_refresh_token, generate_token
from apps.endusers.models import EndUser, UserCategories


# ---------------------------------------------------------------------------
# POST /api/users/register/
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestRegister:
    URL = "/api/users/register/"

    def test_register_success(self, api_client):
        response = api_client.post(self.URL, {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com",
            "mobile": "+919999999901",
        })
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert "user" in data
        assert "user_categories" in data

    def test_register_creates_user_categories_from_system(self, api_client, db):
        Category.objects.create(name="Salary", active=True)
        Category.objects.create(name="Food", active=True)
        response = api_client.post(self.URL, {
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "jane@example.com",
            "mobile": "+919999999902",
        })
        assert response.status_code == status.HTTP_201_CREATED
        assert len(response.json()["user_categories"]) == 2

    def test_register_duplicate_email_returns_400(self, api_client, test_user):
        response = api_client.post(self.URL, {
            "first_name": "Dup",
            "last_name": "User",
            "email": test_user.email,
            "mobile": "+919999999903",
        })
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_missing_fields_returns_400(self, api_client):
        response = api_client.post(self.URL, {})
        assert response.status_code == status.HTTP_400_BAD_REQUEST


# ---------------------------------------------------------------------------
# POST /api/users/login/
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestLogin:
    URL = "/api/users/login/"

    def test_login_success(self, api_client, test_user):
        response = api_client.post(self.URL, {"mobile": test_user.mobile})
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert "user_categories" in data

    def test_login_returns_user_data(self, api_client, test_user):
        response = api_client.post(self.URL, {"mobile": test_user.mobile})
        assert response.json()["user"]["email"] == test_user.email

    def test_login_user_not_found_returns_404(self, api_client):
        response = api_client.post(self.URL, {"mobile": "+910000000000"})
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_login_missing_mobile_returns_400(self, api_client):
        response = api_client.post(self.URL, {})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_login_deactivated_user_returns_403(self, api_client, test_user):
        test_user.is_active = False
        test_user.save()
        response = api_client.post(self.URL, {"mobile": test_user.mobile})
        assert response.status_code == status.HTTP_403_FORBIDDEN


# ---------------------------------------------------------------------------
# POST /api/users/verify-otp/
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestVerifyOtp:
    URL = "/api/users/verify-otp/"

    def test_verify_otp_creates_new_user(self, api_client):
        response = api_client.post(self.URL, {"mobile": "+919111111111", "otp": "111111"})
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert "access_token" in data
        assert data["user_exists"] is False

    def test_verify_otp_existing_user_returns_tokens(self, api_client, test_user):
        response = api_client.post(self.URL, {"mobile": test_user.mobile, "otp": "111111"})
        assert response.status_code == status.HTTP_201_CREATED
        assert "access_token" in response.json()

    def test_verify_otp_wrong_otp_returns_400(self, api_client):
        response = api_client.post(self.URL, {"mobile": "+919111111112", "otp": "000000"})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid OTP" in response.json()["error"]

    def test_verify_otp_missing_mobile_returns_400(self, api_client):
        response = api_client.post(self.URL, {"otp": "111111"})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_verify_otp_missing_otp_returns_400(self, api_client):
        response = api_client.post(self.URL, {"mobile": "+919111111113"})
        assert response.status_code == status.HTTP_400_BAD_REQUEST


# ---------------------------------------------------------------------------
# POST /api/users/refresh-token/
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestRefreshToken:
    URL = "/api/users/refresh-token/"

    def test_refresh_token_success(self, api_client, test_user):
        refresh = generate_refresh_token(test_user)
        response = api_client.post(self.URL, {"refresh_token": refresh})
        assert response.status_code == status.HTTP_200_OK
        assert "access_token" in response.json()

    def test_refresh_token_invalid_returns_401(self, api_client):
        response = api_client.post(self.URL, {"refresh_token": "invalid.token.here"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_refresh_token_missing_returns_400(self, api_client):
        response = api_client.post(self.URL, {})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_refresh_token_deactivated_user_returns_403(self, api_client, test_user):
        refresh = generate_refresh_token(test_user)
        test_user.is_active = False
        test_user.save()
        response = api_client.post(self.URL, {"refresh_token": refresh})
        assert response.status_code == status.HTTP_403_FORBIDDEN


# ---------------------------------------------------------------------------
# GET /api/users/profile/
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestProfile:
    URL = "/api/users/profile/"

    def test_get_profile_success(self, auth_client, test_user):
        response = auth_client.get(self.URL)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["email"] == test_user.email

    def test_get_profile_unauthenticated_returns_401(self, api_client):
        response = api_client.get(self.URL)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ---------------------------------------------------------------------------
# POST /api/users/update-user/
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestUpdateUser:
    URL = "/api/users/update-user/"

    def test_update_user_success(self, auth_client):
        response = auth_client.post(self.URL, {"first_name": "Updated"})
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["first_name"] == "Updated"

    def test_update_user_unauthenticated_returns_401(self, api_client):
        response = api_client.post(self.URL, {"first_name": "Updated"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ---------------------------------------------------------------------------
# POST /api/users/deactivate/
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestDeactivate:
    URL = "/api/users/deactivate/"

    def test_deactivate_success(self, auth_client, test_user):
        response = auth_client.post(self.URL)
        assert response.status_code == status.HTTP_200_OK
        test_user.refresh_from_db()
        assert test_user.is_active is False

    def test_deactivate_unauthenticated_returns_401(self, api_client):
        response = api_client.post(self.URL)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ---------------------------------------------------------------------------
# GET /api/users/user-categories/
# POST /api/users/category/
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestUserCategories:
    LIST_URL = "/api/users/user-categories/"
    CREATE_URL = "/api/users/category/"

    def test_list_returns_user_categories(self, auth_client, user_category):
        response = auth_client.get(self.LIST_URL)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 1

    def test_list_excludes_soft_deleted(self, auth_client, user_category):
        user_category.is_deleted = True
        user_category.save()
        response = auth_client.get(self.LIST_URL)
        assert len(response.json()) == 0

    def test_list_unauthenticated_returns_401(self, api_client):
        response = api_client.get(self.LIST_URL)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_user_category(self, auth_client):
        response = auth_client.post(self.CREATE_URL, {"name": "Rent"})
        assert response.status_code == status.HTTP_201_CREATED
        names = [c["name"] for c in response.json()]
        assert "Rent" in names

    def test_create_returns_full_list(self, auth_client, user_category):
        auth_client.post(self.CREATE_URL, {"name": "Travel"})
        response = auth_client.post(self.CREATE_URL, {"name": "Insurance"})
        assert response.status_code == status.HTTP_201_CREATED
        assert len(response.json()) >= 3

    def test_create_unauthenticated_returns_401(self, api_client):
        response = api_client.post(self.CREATE_URL, {"name": "Rent"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ---------------------------------------------------------------------------
# POST /api/users/update-categories/<uuid>/
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestUpdateUserCategory:
    def test_update_user_category_success(self, auth_client, user_category):
        url = f"/api/users/update-categories/{user_category.id}/"
        response = auth_client.post(url, {"name": "Dining Out"})
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["name"] == "Dining Out"

    def test_update_unauthenticated_returns_401(self, api_client, user_category):
        url = f"/api/users/update-categories/{user_category.id}/"
        response = api_client.post(url, {"name": "Dining Out"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ---------------------------------------------------------------------------
# GET /api/users/delete-category/?id=<uuid>
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestDeleteUserCategory:
    URL = "/api/users/delete-category/"

    def test_delete_soft_deletes_category(self, auth_client, user_category):
        response = auth_client.get(self.URL, {"id": str(user_category.id)})
        assert response.status_code == status.HTTP_200_OK
        user_category.refresh_from_db()
        assert user_category.is_deleted is True

    def test_delete_missing_id_returns_400(self, auth_client):
        response = auth_client.get(self.URL)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_delete_nonexistent_id_returns_404(self, auth_client):
        response = auth_client.get(self.URL, {"id": str(uuid.uuid4())})
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_unauthenticated_returns_401(self, api_client, user_category):
        response = api_client.get(self.URL, {"id": str(user_category.id)})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
