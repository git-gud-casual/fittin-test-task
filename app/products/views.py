import io

from rest_framework import generics, status
from rest_framework.parsers import JSONParser
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import ValidationError
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .serializers import (CategorySerializer, ProductSerializer,
                          GetProductsByCategorySer)
from .models import Category, Product, ProductSize


class CategoryListView(generics.ListAPIView):
    serializer_class = CategorySerializer
    queryset = Category.objects.filter(parent_category_id=None).all()


class ProductRetrieveView(generics.RetrieveAPIView):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()


class ProductListView(generics.ListAPIView):
    serializer_class = ProductSerializer

    class ProductListPagination(PageNumberPagination):
        page_size = 25

    pagination_class = ProductListPagination

    @swagger_auto_schema(request_body=GetProductsByCategorySer,
                         responses={
                             status.HTTP_200_OK: openapi.Schema(
                                 type=openapi.TYPE_OBJECT,
                                 properties={
                                     "count": openapi.Schema(type=openapi.TYPE_INTEGER),
                                     "next": openapi.Schema(type=openapi.FORMAT_URI),
                                     "previous": openapi.Schema(type=openapi.FORMAT_URI),
                                     "results": openapi.Schema(type=openapi.TYPE_STRING,
                                                               title="Products list as in get response")
                                 }
                             ),
                             status.HTTP_404_NOT_FOUND: "Category not found",
                             status.HTTP_400_BAD_REQUEST: "Invalid request body"
                         },
                         manual_parameters=[
                             openapi.Parameter("min_price", openapi.IN_QUERY,
                                               type=openapi.TYPE_INTEGER, default=0),
                             openapi.Parameter("max_price", openapi.IN_QUERY,
                                               type=openapi.TYPE_INTEGER),
                             openapi.Parameter("sort_by", openapi.IN_QUERY,
                                               type=openapi.TYPE_STRING, enum=["price_up", "price_down"],
                                               default="without sort"),
                             openapi.Parameter("page", openapi.IN_QUERY,
                                               type=openapi.TYPE_INTEGER)
                         ])
    def post(self, request: HttpRequest, *args, **kwargs):
        ser = GetProductsByCategorySer(data=JSONParser().parse(io.BytesIO(request.body)))
        ser.is_valid(raise_exception=True)
        category = get_object_or_404(Category, pk=ser.validated_data["category_id"])
        qs = self.get_queryset()
        qs = qs.filter(category_id__in=category.get_self_and_children_ids())
        qs = self.paginator.paginate_queryset(qs, self.request, view=self)
        return self.paginator.get_paginated_response(ProductSerializer(qs, many=True).data)

    @swagger_auto_schema(manual_parameters=[
                             openapi.Parameter("min_price", openapi.IN_QUERY,
                                               type=openapi.TYPE_INTEGER, default=0),
                             openapi.Parameter("max_price", openapi.IN_QUERY,
                                               type=openapi.TYPE_INTEGER),
                             openapi.Parameter("sort_by", openapi.IN_QUERY,
                                               type=openapi.TYPE_STRING, enum=["price_up", "price_down"],
                                               default="without sort"),
                         ])
    def get(self, *args, **kwargs):
        return super().get(*args, **kwargs)

    def get_queryset(self):
        try:
            min_value = int(self.request.query_params.get("min_price", 0))
            max_value = int(self.request.query_params.get("max_price", -1))
            sort_by = self.request.query_params.get("sort_by")
            q = Product.objects.filter(price__gte=min_value).annotate(
                total_count=Sum("sizes__count_in_stock")
            ).filter(total_count__gt=0).order_by("id")
            if max_value >= 0:
                q = q.filter(price__lte=max_value)
            if sort_by == "price_up":
                q = q.order_by("price")
            elif sort_by == "price_down":
                q = q.order_by("-price")
            return q.all()
        except ValueError:
            raise ValidationError({"error": "query param min_value or max_value is not integer"})
