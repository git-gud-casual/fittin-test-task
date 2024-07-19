from django.db import models
from django.core.validators import MinValueValidator

from typing import List


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    displayed_name = models.CharField(max_length=100, unique=True)
    parent_category = models.ForeignKey("self", on_delete=models.SET_NULL,
                                        null=True, related_name="children_categories")

    def get_self_and_children_ids(self) -> List[int]:
        ids = [self.pk]
        for child in self.children_categories.all():
            ids.extend(child.get_self_and_children_ids())
        return ids


class Product(models.Model):
    image = models.URLField()
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    category = models.ForeignKey(Category, on_delete=models.PROTECT,
                                 related_name="products")


class ProductSize(models.Model):
    SIZE_CHOICES = (
        ("s", "S"),
        ("m", "M"),
        ("l", "L")
    )
    size = models.CharField(max_length=2, choices=SIZE_CHOICES)
    product = models.ForeignKey(Product, on_delete=models.CASCADE,
                                related_name="sizes")
    count_in_stock = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ("size", "product")
