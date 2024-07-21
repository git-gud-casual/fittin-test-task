from rest_framework import serializers

from .models import CartEntry, OrderEntry, Order
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


class OrderSerializer(serializers.ModelSerializer):
    order_id = serializers.IntegerField(
        source="id",
        read_only=True
    )
    orders = serializers.ListSerializer(
        child=OrderEntrySerializer(),
        allow_empty=False,
        source="entries"
    )

    class Meta:
        model = Order
        fields = ("order_id", "orders")
        read_only_fields = ("order_id",)
