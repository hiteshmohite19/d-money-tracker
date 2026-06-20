from django.urls import path

from .views import WishlistViewSet

# Wishlist endpoints
wishlist_list = WishlistViewSet.as_view({"get": "list"})
wishlist_create = WishlistViewSet.as_view({"post": "create"})
wishlist_update = WishlistViewSet.as_view({"post": "update_item"})
wishlist_delete = WishlistViewSet.as_view({"get": "delete_item"})

urlpatterns = [
    path("", wishlist_list, name="wishlist-list"),
    path("create/", wishlist_create, name="wishlist-create"),
    path("<uuid:pk>/update/", wishlist_update, name="wishlist-update"),
    path("delete/", wishlist_delete, name="wishlist-delete"),
]
