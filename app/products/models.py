from django.db import models
from django.core.validators import MinValueValidator


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    displayed_name = models.CharField(max_length=100, unique=True)
    parent_category = models.ForeignKey("self", on_delete=models.SET_NULL,
                                        null=True, related_name="children_categories")


class Product(models.Model):
    image = models.URLField()
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    category = models.ForeignKey(Category, on_delete=models.PROTECT,
                                 related_name="products")
