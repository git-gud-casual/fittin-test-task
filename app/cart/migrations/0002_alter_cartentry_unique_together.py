# Generated by Django 4.2.14 on 2024-07-20 02:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0004_alter_productdiscount_discount_count'),
        ('cart', '0001_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='cartentry',
            unique_together={('product', 'cart')},
        ),
    ]
