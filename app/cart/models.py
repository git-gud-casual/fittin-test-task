from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator

from products.models import ProductSize


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,
                                related_name="cart", primary_key=True)
    products = models.ManyToManyField(ProductSize, through="CartEntry")

    def __str__(self):
        return f"{self.user.username}`s cart"


class CartEntry(models.Model):
    product = models.ForeignKey(ProductSize, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    count = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )

    class Meta:
        unique_together = ("product", "cart")
