from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db.models import Sum
from django.utils import timezone

from products.models import ProductSize


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,
                                related_name="cart", primary_key=True)
    products = models.ManyToManyField(ProductSize, through="CartEntry")

    @property
    def final_price(self):
        return sum(self.products.through.all())

    def __str__(self):
        return f"{self.user.username}`s cart"


class CartEntry(models.Model):
    product = models.ForeignKey(ProductSize, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    count = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )

    @property
    def final_price(self) -> int:
        return self.product.product.final_price * self.count

    class Meta:
        unique_together = ("product", "cart")


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name="orders")
    created_at = models.DateTimeField(default=timezone.now)
    payed = models.BooleanField(default=False)

    @property
    def final_price(self):
        return self.entries.aggregate(total=Sum("final_price"))["total"]


class OrderEntry(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="entries")
    product = models.ForeignKey(ProductSize, on_delete=models.PROTECT)
    count = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )
    final_price = models.PositiveIntegerField()

    class Meta:
        unique_together = ("order", "product")
