"""
Root URL configuration for dmoneytracker.

API endpoints live under /api/.
Each app defines its own URL patterns in its urls.py file.
"""

from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/categories/", include("apps.categories.urls")),
    path("api/users/", include("apps.endusers.urls")),
    path("api/subcategories/", include("apps.subcategories.urls")),
    path("api/transactions/", include("apps.transactions.urls")),
    path("api/wishlist/", include("apps.wishlist.urls")),
    # API Documentation
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]

# ---------------------------------------------------------------------------
# Serve media uploads during local development
# ---------------------------------------------------------------------------
if settings.DEBUG:
    from django.conf.urls.static import static

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
