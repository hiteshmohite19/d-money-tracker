from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Category, CategoryTransactions
from .serializers import (
    CategoryListSerializer,
    CategorySerializer,
    CategoryTransactionsRawSerializer,
)


class CategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for Category model."""

    queryset = Category.objects.all()
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if self.action == "list":
            return CategoryListSerializer
        return CategorySerializer

    @action(
        detail=False,
        methods=["get"],
        url_path="category-transactions",
        permission_classes=[IsAuthenticated],
    )
    def categories_transactions(self, request):
        """
        GET /categories/category-transactions/ - Get category transactions for authenticated user.

        Returns category_id and amount (as-is, negative for debits, positive for credits).
        """
        user = request.user
        category_transactions = CategoryTransactions.objects.filter(user_id=user)

        serializer = CategoryTransactionsRawSerializer(category_transactions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)