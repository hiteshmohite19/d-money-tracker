from django.urls import include, path
from rest_framework.routers import DefaultRouter

# from .viewsets import CategoryViewSet

router = DefaultRouter()
# router.register(r"", CategoryViewSet, basename="category")

urlpatterns = [
    path("", include(router.urls)),
]
