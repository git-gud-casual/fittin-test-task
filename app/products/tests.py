from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from json import loads

from .models import Product, Category, ProductSize
from .serializers import CategorySerializer, ProductSerializer


class ProductsTestCase(APITestCase):
    fixtures = ["categories.json"]

    api_client: APIClient

    @classmethod
    def setUpTestData(cls):
        for i in range(26):
            product = Product()
            product.name = "test"
            product.price = i + 1
            product.image = ("https://cdn.britannica.com/70"
                             "/234870-050-D4D024BB/"
                             "Orange-colored-cat-yawns-displaying-teeth.jpg")
            product.description = "test"
            product.category = Category.objects.get(pk=i % 5 + 1)
            product.save()

            size = ProductSize()
            size.size = "m"
            size.count_in_stock = i % 5
            size.product = product
            size.save()

            size = ProductSize()
            size.size = "l"
            size.count_in_stock = 0
            size.product = product
            size.save()

        cls.api_client = APIClient()

    def test_retrieve(self):
        resp = loads(self.api_client.get("/product/1/").content)
        ser1 = ProductSerializer(Product.objects.get(pk=1))
        self.assertDictEqual(ser1.data, resp)

    def test_retrieve404(self):
        for id in (-1, 0, 27):
            code = self.api_client.get(f"/product/{id}/").status_code
            self.assertEqual(status.HTTP_404_NOT_FOUND, code)

    def test_get_list(self):
        resp = loads(self.api_client.get("/products?sort_by=price_down&min_price=7&max_price=20").content)
        self.assertEqual(resp["results"][0]["price"], 20)

    def test_get_list_by_post(self):
        resp = loads(self.api_client.post("/products?sort_by=price_down&min_price=6&max_price=19",
                                          data={"category_id": 2}, format="json").content)
        self.assertEqual(resp["results"][0]["price"], 19)
        self.assertEqual(resp["count"], 11)


class CategoriesTestCase(APITestCase):
    fixtures = ["categories.json"]
    api_client = APIClient()

    def test_get_categories(self):
        categories = CategorySerializer(Category.objects.filter(parent_category_id=None).all(), many=True).data
        resp = loads(self.api_client.get("/categories").content)
        self.assertCountEqual(resp, categories)
