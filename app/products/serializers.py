from rest_framework import serializers
from rest_framework_recursive.fields import RecursiveField

from .models import Category


class CategorySerializer(serializers.ModelSerializer):
    children_categories = RecursiveField(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ("id", "name", "displayed_name", "children_categories")
