from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib import messages
from marketplace.models import Shop, Product
from orders.models import Cart, CartItem

User = get_user_model()


class CartFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="u", password="p")
        self.client.login(username="u", password="p")
        self.shop = Shop.objects.create(owner=self.user, name="S1")
        self.product = Product.objects.create(shop=self.shop, title="P1", price=10, is_active=True)

    def test_add_to_cart_creates_item(self):
        url = reverse("orders:add_to_cart", args=[self.product.id])
        resp = self.client.post(url, {"quantity": 2})
        self.assertEqual(resp.status_code, 302)
        cart = Cart.objects.get(user=self.user, active=True)
        item = CartItem.objects.get(cart=cart, product=self.product)
        self.assertEqual(item.quantity, 2)

    def test_update_quantity(self):
        self.client.post(reverse("orders:add_to_cart", args=[self.product.id]), {"quantity": 1})
        item = CartItem.objects.get()
        resp = self.client.post(reverse("orders:update_quantity", args=[item.id]), {"quantity": 5},
                                HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(resp.status_code, 200)
        item.refresh_from_db()
        self.assertEqual(item.quantity, 5)

    def test_remove_item(self):
        self.client.post(reverse("orders:add_to_cart", args=[self.product.id]), {"quantity": 1})
        item = CartItem.objects.get()
        resp = self.client.post(reverse("orders:remove_item", args=[item.id]),
                                HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(CartItem.objects.count(), 0)

    def test_messages(self):
        resp = self.client.post(reverse("orders:add_to_cart", args=[self.product.id]), {"quantity": 1})
        msgs = list(messages.get_messages(resp.wsgi_request))
        self.assertEqual(len(msgs), 1)
        self.assertEqual(str(msgs[0]), "Added 1 × P1 to your cart.")
