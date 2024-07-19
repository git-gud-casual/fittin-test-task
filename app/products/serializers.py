from rest_framework import serializers
from rest_framework_recursive.fields import RecursiveField

from .models import Category, Product, ProductSize, ProductDiscount


class CategorySerializer(serializers.ModelSerializer):
    children_categories = RecursiveField(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ("id", "name", "displayed_name", "children_categories")


class SizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSize
        fields = ("size", "count_in_stock")


class ProductSerializer(serializers.ModelSerializer):
    category_id = serializers.PrimaryKeyRelatedField(source="category.id",
                                                     queryset=Category.objects.all())
    sizes = SizeSerializer(many=True, read_only=True)
    discount = serializers.SlugRelatedField(slug_field="discount_count",
                                            queryset=ProductDiscount.objects.all(),
                                            required=False)
    final_price = serializers.SerializerMethodField()

    def get_final_price(self, obj) -> int:
        return obj.final_price

    class Meta:
        model = Product
        fields = ("id", "image", "name", "description",
                  "price", "category_id", "sizes", "discount",
                  "final_price")


class GetProductsByCategorySer(serializers.Serializer):
    category_id = serializers.IntegerField()
