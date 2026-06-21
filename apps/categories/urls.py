from django.urls import include, path
from rest_framework.routers import DefaultRouter
from apps.categories.viewsets import CategoryViewSet
# from .viewsets import CategoryViewSet

router = DefaultRouter()
category_transactions = CategoryViewSet.as_view({"get": "categories_transactions"})
urlpatterns = [
    path("category-transactions/", category_transactions, name="category-transactions"),
]
