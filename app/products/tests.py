from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from json import loads

from .models import Product, Category
from .serializers import CategorySerializer, ProductSerializer


class ProductsTestCase(APITestCase):
    fixtures = ["categories.json"]

    api_client: APIClient

    @classmethod
    def setUpTestData(cls):
        product = Product()
        product.name = "test"
        product.price = 1
        product.image = ("https://cdn.britannica.com/70"
                         "/234870-050-D4D024BB/"
                         "Orange-colored-cat-yawns-displaying-teeth.jpg")
        product.description = "test"
        product.category = Category.objects.get(pk=1)
        product.save()

        cls.api_client = APIClient()

    def test_retrieve(self):
        resp = loads(self.api_client.get("/product/1/").content)
        ser1 = ProductSerializer(Product.objects.get(pk=1))
        self.assertDictEqual(ser1.data, resp)

    def test_retrieve404(self):
        for id in (-1, 0, 2, 3):
            code = self.api_client.get(f"/product/{id}/").status_code
            self.assertEqual(status.HTTP_404_NOT_FOUND, code)


class CategoriesTestCase(APITestCase):
    fixtures = ["categories.json"]
    api_client = APIClient()

    def test_get_categories(self):
        categories = CategorySerializer(Category.objects.filter(parent_category_id=None).all(), many=True).data
        resp = loads(self.api_client.get("/categories").content)
        self.assertCountEqual(resp, categories)
