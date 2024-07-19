from rest_framework import generics

from .serializers import CategorySerializer, ProductSerializer
from .models import Category, Product


class CategoryListView(generics.ListAPIView):
    serializer_class = CategorySerializer
    queryset = Category.objects.filter(parent_category_id=None).all()


class ProductRetrieveView(generics.RetrieveAPIView):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
