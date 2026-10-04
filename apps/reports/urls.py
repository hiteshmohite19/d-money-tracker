from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import ReportViewSet

router = SimpleRouter()
router.register(r"", ReportViewSet, basename="reports")

urlpatterns = [
    path("", include(router.urls)),
]
