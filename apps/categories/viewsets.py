from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action

from .models import Category
from .serializers import CategoryListSerializer, CategorySerializer


class CategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for Category model."""

    queryset = Category.objects.all()
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if self.action == "list":
            return CategoryListSerializer
        return CategorySerializer
    
    @action(detail=False, methods=['get'], url_path='/categroies')
    def categories_transactions():
        pass