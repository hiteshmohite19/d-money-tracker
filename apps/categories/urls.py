from django.urls import path
from rest_framework.permissions import IsAuthenticated

from apps.categories.viewsets import CategoryViewSet

category_transactions = CategoryViewSet.as_view(
    {"get": "categories_transactions"},
    permission_classes=[IsAuthenticated],
)
urlpatterns = [
    path("category-transactions/", category_transactions, name="category-transactions"),
]
