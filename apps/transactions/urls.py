from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .viewsets import TransactionViewSet

router = SimpleRouter()
# router.register(r"", TransactionViewSet, basename="transaction")

# Custom Transaction endpoints
transaction_list = TransactionViewSet.as_view({"get": "list"})
transaction_create = TransactionViewSet.as_view({"post": "create_transaction"})
transaction_update = TransactionViewSet.as_view({"post": "update_transaction"})
transaction_delete = TransactionViewSet.as_view({"get": "delete_transaction"})

urlpatterns = [
    # Custom endpoints
    path("transactions/", transaction_list, name="transaction-list"),
    path("transaction/", transaction_create, name="transaction-create"),
    path("transaction/<uuid:pk>/", transaction_update, name="transaction-update"),
    path("delete-transaction/<uuid:pk>/", transaction_delete, name="transaction-delete"),
    # Default router
    path("", include(router.urls)),
]
