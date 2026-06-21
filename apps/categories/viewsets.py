from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Category, CategoryTransactions
from .serializers import (
    CategoryListSerializer,
    CategorySerializer,
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
        GET /categories/{user_category_id}/category-transactions/ - Get category transactions for authenticated user.

        Returns category_id and amount (as-is, negative for debits, positive for credits).
        Includes all user categories, even those without transactions (amount 0.0).
        """
        from apps.endusers.models import UserCategories
        from decimal import Decimal

        user = request.user

        # Get all user categories (not deleted)
        user_categories = UserCategories.objects.filter(
            user_id=user.id,
            is_deleted=False,
        )

        # Get existing category transactions
        category_transactions = CategoryTransactions.objects.filter(user_id=user)

        # Create a dictionary mapping category_id to amount
        transactions_dict = {ct.category_id_id: ct.amount for ct in category_transactions}

        # Build response data with all categories
        response_data = []
        for category in user_categories:
            amount = transactions_dict.get(category.id, Decimal("0.00"))
            response_data.append(
                {
                    "category_id": category.id,
                    "amount": amount,
                }
            )

        return Response(response_data, status=status.HTTP_200_OK)
