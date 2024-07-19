# Generated by Django 4.2.14 on 2024-07-19 20:14

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('products', '0002_productsize'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductDiscount',
            fields=[
                ('product', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='discount', serialize=False, to='products.product')),
                ('discount_count', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(100)])),
            ],
        ),
        migrations.AddField(
            model_name='product',
            name='favourite_for_users',
            field=models.ManyToManyField(related_name='favourites', to=settings.AUTH_USER_MODEL),
        ),
    ]
