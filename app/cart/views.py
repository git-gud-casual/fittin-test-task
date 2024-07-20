from rest_framework import generics, mixins, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.shortcuts import get_object_or_404

from .serializers import CartEntrySerializer
from .models import CartEntry, ProductSize


class CartListCreateView(generics.ListCreateAPIView):
    serializer_class = CartEntrySerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        if self.request.user.is_anonymous:
            return
        return CartEntry.objects.filter(cart=self.request.user.cart).all()

    def perform_create(self, serializer):
        data = serializer.validated_data
        product = get_object_or_404(ProductSize, product_id=data["product"]["product_id"],
                                    size=data["product"]["size"])
        try:
            cart_entry = CartEntry.objects.get(
                cart=self.request.user.cart,
                product=product
            )
            cart_entry.count += data["count"]
            cart_entry.save()
        except CartEntry.DoesNotExist:
            CartEntry.objects.create(cart=self.request.user.cart,
                                     product=product,
                                     count=data["count"])


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
        product = get_object_or_404(ProductSize, product_id=data["product"]["product_id"],
                                    size=data["product"]["size"])
        try:
            cart_entry = CartEntry.objects.get(
                cart=self.request.user.cart,
                product=product
            )
            cart_entry.count += data["count"]
            cart_entry.save()
        except CartEntry.DoesNotExist:
            CartEntry.objects.create(cart=self.request.user.cart,
                                     product=product,
                                     count=data["count"])

    def perform_update(self, serializer):
        data = serializer.validated_data
        product = get_object_or_404(ProductSize, product_id=data["product"]["product_id"],
                                    size=data["product"]["size"])
        cart_entry = self.get_object()
        cart_entry.product = product
        cart_entry.count = data["count"]
        cart_entry.save()

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        filter_kwargs = {f"product__{lookup_field}": self.kwargs[lookup_field]
                         for lookup_field in self.lookup_fields}
        obj = get_object_or_404(queryset, **filter_kwargs)
        self.check_object_permissions(self.request, obj)
        return obj
