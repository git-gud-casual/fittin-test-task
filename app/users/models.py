from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from cart.models import Cart


@receiver(post_save, sender=User)
def create_basket(instance: User, created: bool, **_):
    if created:
        Cart.objects.create(user=instance)
