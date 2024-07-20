from rest_framework import serializers

from .models import CartEntry
from products.models import ProductSize


class CartEntrySerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(
        source="product.product_id"
    )
    size = serializers.ChoiceField(
        choices=ProductSize.SIZE_CHOICES,
        source="product.size"
    )

    class Meta:
        model = CartEntry
        fields = ("count", "product_id", "size")
