from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.signals import post_save
from celery import shared_task
from django.core.mail import send_mail

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

    def __str__(self):
        return self.displayed_name


class Product(models.Model):
    image = models.URLField()
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    category = models.ForeignKey(Category, on_delete=models.PROTECT,
                                 related_name="products")
    favourite_for_users = models.ManyToManyField(User, related_name="favourites",
                                                 blank=True)

    @property
    def final_price(self) -> int:
        try:
            price = self.price - int(self.price * (self.discount.discount_count / 100))
        except ProductDiscount.DoesNotExist:
            price = self.price
        return price

    def __str__(self):
        return self.name


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

    def __str__(self):
        return f"Product {self.product.id} Size {self.size}"


class ProductDiscount(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, primary_key=True,
                                   related_name="discount")
    discount_count = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(99)]
    )

    @staticmethod
    def send_emails_when_save(sender, instance: "ProductDiscount", **__):
        send_discount_for_users.delay(instance.pk)


post_save.connect(ProductDiscount.send_emails_when_save, sender=ProductDiscount)


@shared_task
def send_discount_for_users(discount_id: int):
    discount = ProductDiscount.objects.get(pk=discount_id)
    subject = "Скидка"
    message = (f"Скидка на отслеживаемый товар {discount.product.name}.\n"
               f"Скидка {discount.discount_count}%. Финальная цена {discount.product.final_price}")
    users_emails = discount.product.favourite_for_users.values_list("email", flat=True)
    send_mail(subject, message,
              recipient_list=users_emails, from_email=None)
