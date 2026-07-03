from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import EndUserViewSet, UserCategoryViewSet

router = SimpleRouter()

# User Category endpoints
user_category_list = UserCategoryViewSet.as_view({"get": "list"})
user_category_create = UserCategoryViewSet.as_view({"post": "create"})
user_category_update = UserCategoryViewSet.as_view({"post": "update_category"})
user_category_delete = UserCategoryViewSet.as_view({"get": "delete_category"})

# EndUser endpoints
user_verify_otp = EndUserViewSet.as_view({"post": "verify_otp"})
user_update = EndUserViewSet.as_view({"post": "update_user"})
user_deactivate = EndUserViewSet.as_view({"post": "deactivate"})
user_get = EndUserViewSet.as_view({"get": "get_user"})

urlpatterns = [
    # EndUser endpoints
    path("verify-otp/", user_verify_otp, name="user-verify-otp"),
    path("update-user/", user_update, name="user-update"),
    path("deactivate/", user_deactivate, name="user-deactivate"),
    path("profile/", user_get, name="user-get"),
    # User Categories endpoints
    path("user-categories/", user_category_list, name="user-categories-list"),
    path("category/", user_category_create, name="user-category-create"),
    path("update-categories/<uuid:pk>/", user_category_update, name="user-category-update"),
    path("delete-category/", user_category_delete, name="user-category-delete"),
    # EndUser router
    path("", include(router.urls)),
]
