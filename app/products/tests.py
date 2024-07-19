from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from json import loads

from .models import Product, Category, ProductSize, ProductDiscount
from .serializers import CategorySerializer, ProductSerializer


class ProductsTestCase(APITestCase):
    fixtures = ["categories.json"]

    api_client: APIClient

    @classmethod
    def setUpTestData(cls):
        for i in range(60):
            product = Product()
            product.name = "test"
            product.price = i + 1
            product.image = ("https://cdn.britannica.com/70"
                             "/234870-050-D4D024BB/"
                             "Orange-colored-cat-yawns-displaying-teeth.jpg")
            product.description = "test"
            product.category = Category.objects.get(pk=i % 5 + 1)
            product.save()

            # Создание размеров для каждого не 5ого продукта
            # так же создание продукта отсутствующего на складах для каждого 10ого
            if i % 5 != 0 or i % 2 == 0:
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

            if i % 2 == 0:
                discount = ProductDiscount()
                discount.product = product
                discount.discount_count = i + 1
                discount.save()

        cls.api_client = APIClient()

    def test_retrieve(self):
        resp = loads(self.api_client.get("/product/1/").content)
        ser1 = ProductSerializer(Product.objects.get(pk=1))
        self.assertDictEqual(ser1.data, resp)
        self.assertEqual(sum([size["count_in_stock"] for size in resp["sizes"]]), 0)

    def test_retrieve2(self):
        resp = loads(self.api_client.get("/product/5/").content)
        ser1 = ProductSerializer(Product.objects.get(pk=5))
        self.assertDictEqual(ser1.data, resp)
        self.assertEqual(sum([size["count_in_stock"] for size in resp["sizes"]]), 4)

    def test_retrieve404(self):
        for id in (-1, 0, 61):
            code = self.api_client.get(f"/product/{id}/").status_code
            self.assertEqual(status.HTTP_404_NOT_FOUND, code)

    def test_get_list(self):
        resp = loads(self.api_client.get("/products?sort_by=price_down&page=2").content)
        self.assertEqual(resp["results"][-1]["final_price"], 2)
        prices = [pr["final_price"] for pr in resp["results"]]
        prices_sorted = sorted(prices.copy(), reverse=True)
        self.assertListEqual(prices_sorted, prices)
        resp = loads(self.api_client.get("/products?sort_by=price_down").content)
        prices = [pr["final_price"] for pr in resp["results"]]
        prices_sorted = sorted(prices.copy(), reverse=True)
        self.assertListEqual(prices_sorted, prices)

    def test_get_list_by_post(self):
        resp = loads(self.api_client.post("/products?sort_by=price_down&min_price=6&max_price=19",
                                          data={"category_id": 2}, format="json").content)
        self.assertEqual(resp["results"][0]["final_price"], 18)
        self.assertEqual(resp["count"], 11)
        prices = [pr["final_price"] for pr in resp["results"]]
        prices_sorted = sorted(prices.copy(), reverse=True)
        self.assertListEqual(prices_sorted, prices)


class CategoriesTestCase(APITestCase):
    fixtures = ["categories.json"]
    api_client = APIClient()

    def test_get_categories(self):
        categories = CategorySerializer(Category.objects.filter(parent_category_id=None).all(), many=True).data
        resp = loads(self.api_client.get("/categories").content)
        self.assertCountEqual(resp, categories)
