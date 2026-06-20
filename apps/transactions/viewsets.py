from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Transaction
from .serializers import (
    TransactionCreateUpdateSerializer,
    TransactionListSerializer,
    TransactionSerializer,
)


class TransactionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Transaction model (requires JWT authentication).

    Endpoints:
    - GET /transactions/ - List all transactions for authenticated user
    - POST /transaction/ - Create new transaction
    - POST /transaction/{id}/ - Update transaction
    - GET /delete-transaction/{id}/ - Soft delete transaction
    """

    queryset = Transaction.objects.filter(is_deleted=False)
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "list":
            return TransactionListSerializer
        if self.action in ["create", "update", "partial_update", "create_transaction", "update_transaction"]:
            return TransactionCreateUpdateSerializer
        return TransactionSerializer

    def get_queryset(self):
        """Return transactions for authenticated user, excluding soft deleted."""
        return Transaction.objects.filter(
            user_id=self.request.user.id,
            is_deleted=False,
        ).select_related("user_category", "sub_category").order_by("-date", "-created_at")

    def list(self, request, *args, **kwargs):
        """GET /transactions/ - List all transactions for authenticated user."""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["post"], url_path="create")
    def create_transaction(self, request):
        """
        POST /transaction/ - Create a new transaction.

        Note: User's available_balance and CategoryTransactions are updated
        automatically via signals.

        Returns all transactions for the user after creation.
        """
        user = request.user
        data = request.data.copy()
        data["user_id"] = str(user.id)

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save(created_by=user.id)

        # Return all transactions for the user
        all_transactions = self.get_queryset()
        response_serializer = TransactionListSerializer(all_transactions, many=True)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="update")
    def update_transaction(self, request, pk=None):
        """POST /transaction/{id}/ - Update a transaction."""
        user = request.user
        try:
            instance = Transaction.objects.get(
                id=pk,
                user_id=user.id,
                is_deleted=False,
            )
        except Transaction.DoesNotExist:
            return Response(
                {"error": "Transaction not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        data = request.data.copy()
        data["user_id"] = str(user.id)

        serializer = self.get_serializer(instance, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=user.id)

        response_serializer = TransactionSerializer(serializer.instance)
        return Response(response_serializer.data)

    @action(detail=True, methods=["get"], url_path="delete")
    def delete_transaction(self, request, pk=None):
        """GET /delete-transaction/{id}/ - Soft delete a transaction."""
        user = request.user
        try:
            instance = Transaction.objects.get(
                id=pk,
                user_id=user.id,
                is_deleted=False,
            )
        except Transaction.DoesNotExist:
            return Response(
                {"error": "Transaction not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        instance.is_deleted = True
        instance.updated_by = user.id
        instance.save()

        return Response(
            {"message": "Transaction deleted successfully"},
            status=status.HTTP_200_OK,
        )
