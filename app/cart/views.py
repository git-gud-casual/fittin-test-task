from rest_framework import mixins, viewsets, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import ValidationError
from django.db import transaction
from django.shortcuts import get_object_or_404

from .serializers import CartEntrySerializer, OrderEntrySerializer, OrderSerializer
from .models import CartEntry, ProductSize, OrderEntry, Order


class CartViewSet(viewsets.GenericViewSet,
                  mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  mixins.DestroyModelMixin,
                  mixins.UpdateModelMixin):
    serializer_class = CartEntrySerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    lookup_fields = ("product_id", "size")

    def get_queryset(self):
        if self.request.user.is_anonymous:
            return
        return CartEntry.objects.filter(cart=self.request.user.cart).all()

    def get_object(self):
        super().get_object()

    def perform_create(self, serializer):
        data = serializer.validated_data
        try:
            product = ProductSize.objects.get(product_id=data["product"]["product_id"],
                                              size=data["product"]["size"])
            try:
                cart_entry = CartEntry.objects.get(
                    cart=self.request.user.cart,
                    product=product
                )
                cart_entry.count += data["count"]
                cart_entry.save()
            except CartEntry.DoesNotExist:
                cart_entry = CartEntry.objects.create(cart=self.request.user.cart,
                                                      product=product,
                                                      count=data["count"])
            serializer.instance = cart_entry
        except ProductSize.DoesNotExist:
            raise ValidationError({"message": "productsize does not exist"})

    def perform_update(self, serializer):
        data = serializer.validated_data
        try:
            product = ProductSize.objects.get(product_id=data["product"]["product_id"],
                                              size=data["product"]["size"])
            cart_entry = self.get_object()
            cart_entry.product = product
            cart_entry.count = data["count"]
            cart_entry.save()
            serializer.instance = cart_entry
        except ProductSize.DoesNotExist:
            raise ValidationError({"message": "productsize does not exist"})

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        filter_kwargs = {f"product__{lookup_field}": self.kwargs[lookup_field]
                         for lookup_field in self.lookup_fields}
        obj = get_object_or_404(queryset, **filter_kwargs)
        self.check_object_permissions(self.request, obj)
        return obj


class OrderView(generics.CreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def perform_create(self, serializer: OrderEntrySerializer):
        entries_data = serializer.validated_data["entries"]
        qs = CartEntry.objects.filter(cart=self.request.user.cart)
        try:
            entries = [qs.get(product__product_id=data["product"]["product_id"],
                              product__size=data["product"]["size"]) for data in entries_data]

            with transaction.atomic():
                order = Order.objects.create(
                    user=self.request.user
                )
                order_entries = []
                for entry in entries:
                    if entry.product.count_in_stock < entry.count:
                        raise ValidationError({"message": "order count bigger than count in stock"})
                    order_entry = OrderEntry(
                        order=order,
                        product=entry.product,
                        count=entry.count,
                        final_price=entry.final_price
                    )
                    entry.product.count_in_stock -= entry.count
                    entry.product.save()
                    entry.delete()
                    order_entries.append(order_entry)
                OrderEntry.objects.bulk_create(
                    order_entries
                )
                serializer.instance = order
        except CartEntry.DoesNotExist:
            raise ValidationError({"message": "not in cart"})
