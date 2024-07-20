from django.contrib import admin

from .models import CartEntry, Order, OrderEntry


@admin.register(CartEntry)
class CartEntryAdmin(admin.ModelAdmin):
    list_display = ["cart", "product", "count"]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["user", "created_at", "payed", "final_price"]

    def picture_image(self, obj: Order):
        return obj.final_price

    def has_add_permission(self, request):
        return False


@admin.register(OrderEntry)
class OrderEntryAdmin(admin.ModelAdmin):
    list_display = ["order", "product", "count", "final_price"]
