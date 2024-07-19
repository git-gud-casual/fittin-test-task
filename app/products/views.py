from rest_framework import generics

from .serializers import CategorySerializer
from .models import Category


class CategoryListView(generics.ListAPIView):
    serializer_class = CategorySerializer
    queryset = Category.objects.filter(parent_category_id=None).all()
