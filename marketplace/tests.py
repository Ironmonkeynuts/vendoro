from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from marketplace.models import Shop, Product, Inventory


User = get_user_model()


class SellerInventoryTests(TestCase):
    def setUp(self):
        self.seller = User.objects.create_user(
            username="seller",
            password="pword",
            email="seller@example.com",
        )
        self.shop = Shop.objects.create(owner=self.seller, name="Shop 1")
        self.product = Product.objects.create(
            shop=self.shop,
            title="Widget",
            price="9.99",
            is_active=True,
        )
        self.inventory = Inventory.objects.create(
            product=self.product,
            quantity=5,
            low_stock_threshold=2,
        )

        self.client.login(username="seller", password="pword")

    def test_seller_can_update_inventory(self):
        url = reverse(
            "marketplace:seller_update_inventory",
            args=[self.product.id],
        )
        resp = self.client.post(
            url,
            {"quantity": "12", "low_stock_threshold": "3"},
            follow=True,
        )
        self.assertEqual(resp.status_code, 200)
        self.inventory.refresh_from_db()
        self.assertEqual(self.inventory.quantity, 12)
        self.assertEqual(self.inventory.low_stock_threshold, 3)

    def test_cannot_update_with_invalid_quantity(self):
        url = reverse(
            "marketplace:seller_update_inventory",
            args=[self.product.id],
        )
        resp = self.client.post(url, {"quantity": "-5"})
        self.assertEqual(resp.status_code, 302)
        self.inventory.refresh_from_db()
        self.assertEqual(self.inventory.quantity, 5)

    def test_other_users_cannot_update_inventory(self):
        other = User.objects.create_user(username="other", password="12345")
        self.client.logout()
        self.client.login(username="other", password="12345")
        url = reverse(
            "marketplace:seller_update_inventory",
            args=[self.product.id],
        )
        resp = self.client.post(url, {"quantity": "4"})
        self.assertEqual(resp.status_code, 404)
        self.inventory.refresh_from_db()
        self.assertEqual(self.inventory.quantity, 5)
