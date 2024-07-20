from rest_framework import serializers

from .models import CartEntry, OrderEntry
from products.models import ProductSize


class CartEntrySerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(
        source="product.product_id"
    )
    size = serializers.ChoiceField(
        choices=ProductSize.SIZE_CHOICES,
        source="product.size"
    )
    final_price = serializers.SerializerMethodField()

    def get_final_price(self, obj: CartEntry):
        return obj.final_price

    class Meta:
        model = CartEntry
        fields = ("count", "product_id", "size", "final_price")


class OrderEntrySerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(
        source="product.product_id"
    )
    size = serializers.ChoiceField(
        choices=ProductSize.SIZE_CHOICES,
        source="product.size"
    )

    class Meta:
        model = OrderEntry
        fields = ("product_id", "size")
