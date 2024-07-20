from django.contrib import admin

from .models import CartEntry


@admin.register(CartEntry)
class CartEntryAdmin(admin.ModelAdmin):
    list_display = ["cart", "product", "count"]
