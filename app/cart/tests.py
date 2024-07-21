from rest_framework.test import APITestCase, APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from rest_framework import status
from json import loads

from products.models import Product, ProductSize, Category, ProductDiscount
from .models import CartEntry


class ProductsTestCase(APITestCase):
    fixtures = ["categories.json"]
    api_client: APIClient

    @classmethod
    def setUpTestData(cls):
        post_save.disconnect(ProductDiscount.send_emails_when_save, sender=ProductDiscount)

    def setUp(self):
        self.user = User.objects.create_user(username="test",
                                             password="test")
        token = RefreshToken.for_user(self.user)
        self.api_client = APIClient()
        self.api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token.access_token}")
        product1 = Product()
        product1.name = "test"
        product1.price = 1000
        product1.image = ("https://cdn.britannica.com/70"
                          "/234870-050-D4D024BB/"
                          "Orange-colored-cat-yawns-displaying-teeth.jpg")
        product1.description = "test"
        product1.category = Category.objects.get(id=1)
        product1.save()

        product2 = Product()
        product2.name = "test2"
        product2.price = 1500
        product2.image = ("https://cdn.britannica.com/70"
                          "/234870-050-D4D024BB/"
                          "Orange-colored-cat-yawns-displaying-teeth.jpg")
        product2.description = "test"
        product2.category = Category.objects.get(id=3)
        product2.save()

        disc = ProductDiscount()
        disc.product = product1
        disc.discount_count = 50
        disc.save()

        self.product1 = product1
        self.product2 = product2

        self.sizes = ProductSize.objects.bulk_create((
            ProductSize(size="s", product=product1, count_in_stock=100),
            ProductSize(size="m", product=product1, count_in_stock=100),
            ProductSize(size="l", product=product1, count_in_stock=100),
            ProductSize(size="m", product=product2, count_in_stock=100),
            ProductSize(size="l", product=product2, count_in_stock=100)
        ))

        self.cart_entries = CartEntry.objects.bulk_create((
            CartEntry(product=self.sizes[0], cart=self.user.cart, count=2),
            CartEntry(product=self.sizes[-1], cart=self.user.cart, count=5),
        ))

    def test_get1(self):
        value = [
            {
                "product_id": self.product1.id,
                "size": "s",
                "count": 2,
                "final_price": self.product1.final_price * 2
            },
            {
                "product_id": self.product2.id,
                "size": "l",
                "count": 5,
                "final_price": self.product2.final_price * 5
            },
        ]
        resp = loads(self.api_client.get("/cart").content)
        self.assertCountEqual(value, resp)

    def test_get2(self):
        self.user.cart.products.clear()
        value = []
        resp = loads(self.api_client.get("/cart").content)
        self.assertCountEqual(value, resp)

    def test_post1(self):
        size = self.sizes[1]
        body = {
            "product_id": size.product.id,
            "size": size.size,
            "count": 1
        }
        code = self.api_client.post("/cart", body, format="json").status_code
        self.assertEqual(status.HTTP_201_CREATED, code)
        new_entry = self.user.cart.products.through.objects.get(product=size)
        self.assertEqual(new_entry.product.product_id, body["product_id"])
        self.assertEqual(new_entry.product.size, body["size"])
        self.assertEqual(new_entry.count, body["count"])

    def test_post2(self):
        size = self.sizes[1]
        body = {
            "product_id": size.product.id,
            "size": size.size,
            "count": 0
        }
        code = self.api_client.post("/cart", body, format="json").status_code
        self.assertEqual(status.HTTP_400_BAD_REQUEST, code)
        body = {
            "product_id": size.product.id,
            "size": size.size,
            "count": -1
        }
        code = self.api_client.post("/cart", body, format="json").status_code
        self.assertEqual(status.HTTP_400_BAD_REQUEST, code)

    def test_post3(self):
        size = self.sizes[0]
        body = {
            "product_id": size.product.id,
            "size": size.size,
            "count": 1
        }
        code = self.api_client.post("/cart", body, format="json").status_code
        self.assertEqual(status.HTTP_201_CREATED, code)
        entry = self.user.cart.products.through.objects.get(product=size)
        self.assertEqual(entry.count, 3)

    def test_post4(self):
        body = {
            "product_id": self.product2.id,
            "size": "s",
            "count": 1
        }
        code = self.api_client.post("/cart", body, format="json").status_code
        self.assertEqual(status.HTTP_400_BAD_REQUEST, code)

    def test_put(self):
        size = self.sizes[0]
        body = {
            "product_id": size.product_id,
            "size": size.size,
            "count": 10
        }
        code = self.api_client.put(f"/cart/{size.product_id}/{size.size}",
                                   body, format="json").status_code
        self.assertEqual(status.HTTP_200_OK, code)
        entry = self.user.cart.products.through.objects.get(product=size)
        self.assertEqual(entry.count, 10)

    def test_delete(self):
        size = self.sizes[0]
        code = self.api_client.delete(f"/cart/{size.product_id}/{size.size}").status_code
        self.assertEqual(status.HTTP_204_NO_CONTENT, code)
        with self.assertRaises(CartEntry.DoesNotExist):
            _ = self.user.cart.products.through.objects.get(product=size)

    def test_unauthorized(self):
        api_client = APIClient()
        code = api_client.get("/cart").status_code
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, code)
        code = api_client.put("/cart/1/m").status_code
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, code)
        code = api_client.post("/cart").status_code
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, code)
        code = api_client.delete("/cart/1/m").status_code
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, code)

    def test_order1(self):
        code = self.api_client.post("/order", {"orders": []}, format="json").status_code
        self.assertEqual(status.HTTP_400_BAD_REQUEST, code)

    def test_order2(self):
        size = self.sizes[0]
        body = {"orders": [
            {
                "product_id": size.product.id,
                "size": size.size
            }
        ]}
        entry = self.user.cart.products.through.objects.get(product=size)
        resp = self.api_client.post("/order", body, format="json")
        self.assertIsNotNone(loads(resp.content).get("order_id"))
        code = resp.status_code
        self.assertEqual(status.HTTP_201_CREATED, code)
        self.assertEqual(self.user.orders.first().final_price, entry.final_price)
        with self.assertRaises(CartEntry.DoesNotExist):
            _ = self.user.cart.products.through.objects.get(product=size)
        old_count = size.count_in_stock
        size.refresh_from_db()
        self.assertEqual(size.count_in_stock, old_count - entry.count)

    def test_order3(self):
        size1, size2 = self.sizes[0], self.sizes[-1]
        body = {"orders": [
            {
                "product_id": size1.product.id,
                "size": size1.size
            },
            {
                "product_id": size2.product.id,
                "size": size2.size
            }
        ]}
        final_price = self.user.cart.final_price
        resp = self.api_client.post("/order", body, format="json")
        self.assertIsNotNone(loads(resp.content).get("order_id"))
        code = resp.status_code
        self.assertEqual(status.HTTP_201_CREATED, code)
        for entry in self.cart_entries:
            size = entry.product
            with self.assertRaises(CartEntry.DoesNotExist):
                _ = self.user.cart.products.through.objects.get(product=size)
            old_count = size.count_in_stock
            size.refresh_from_db()
            self.assertEqual(size.count_in_stock, old_count - entry.count)
        self.assertEqual(self.user.orders.first().final_price, final_price)

    def test_order4(self):
        size = self.sizes[-1]
        size.count_in_stock = 0
        size.save()
        body = {"orders": [
            {
                "product_id": size.product.id,
                "size": size.size
            }
        ]}
        code = self.api_client.post("/order", body, format="json").status_code
        self.assertEqual(status.HTTP_400_BAD_REQUEST, code)

    def test_order5(self):
        size = self.sizes[-1]
        body = {
            "orders": [
                {
                    "product_id": size.product.id,
                    "size": "s"
                }
            ]
        }
        code = self.api_client.post("/order", body, format="json").status_code
        self.assertEqual(status.HTTP_400_BAD_REQUEST, code)

    def test_order_unathorized(self):
        api_client = APIClient()
        code = api_client.post("/order").status_code
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, code)
