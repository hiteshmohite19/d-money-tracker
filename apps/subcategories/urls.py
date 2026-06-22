from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .viewsets import SubCategoryViewSet

router = SimpleRouter()
# router.register(r"", SubCategoryViewSet, basename="subcategory")

# Custom SubCategory endpoints
sub_category_list_by_user_category = SubCategoryViewSet.as_view({"get": "list_by_user_category"})
sub_category_create = SubCategoryViewSet.as_view({"post": "create_sub_category"})
sub_category_update = SubCategoryViewSet.as_view({"post": "update_sub_category"})
sub_category_delete = SubCategoryViewSet.as_view({"get": "delete_sub_category"})

urlpatterns = [
    # Custom endpoints
    path(
        "<uuid:user_category_id>/sub-categories/",
        sub_category_list_by_user_category,
        name="subcategory-list-by-user-category",
    ),
    path("sub-category/", sub_category_create, name="subcategory-create"),
    path("sub-category/<uuid:pk>/", sub_category_update, name="subcategory-update"),
    path("delete-sub-category/<uuid:pk>/", sub_category_delete, name="subcategory-delete"),
    # Default router
    path("", include(router.urls)),
]
