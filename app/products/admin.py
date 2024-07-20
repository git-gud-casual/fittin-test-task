from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Product, ProductDiscount, ProductSize


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["id", "picture_image", "name", "description"]

    def picture_image(self, obj: Product):
        return mark_safe(f'<img src="{obj.image or ""}" width="150" height="150" /> ')


@admin.register(ProductDiscount)
class ProductDiscountAdmin(admin.ModelAdmin):
    list_display = ["product_id", "discount_count"]


@admin.register(ProductSize)
class ProductsSizeAdmin(admin.ModelAdmin):
    list_display = ["product", "size", "count_in_stock"]