from decimal import Decimal
from unittest.mock import patch

from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.contrib.auth import get_user_model

from marketplace.models import Shop, Product, Inventory
from orders.models import Cart, CartItem, Order, OrderItem
from payments.webhook_handler import StripeWH_Handler


User = get_user_model()


class CheckoutInventoryAdjustmentTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username="buyer", password="pw")
        self.shop = Shop.objects.create(owner=self.user, name="Shop 1")
        self.product = Product.objects.create(
            shop=self.shop,
            title="Widget",
            price=Decimal("10.00"),
            is_active=True,
        )
        self.inventory = Inventory.objects.create(
            product=self.product,
            quantity=10,
            low_stock_threshold=2,
        )
        self.cart = Cart.objects.create(user=self.user, active=True)
        CartItem.objects.create(cart=self.cart, product=self.product, quantity=3)
        self.order = Order.objects.create(
            user=self.user,
            shop=self.shop,
            total_amount=Decimal("30.00"),
            status=Order.Status.PENDING,
        )
        OrderItem.objects.create(
            order=self.order,
            product=self.product,
            unit_price=Decimal("10.00"),
            quantity=3,
        )

    def _event_payload(self):
        return {
            "data": {
                "object": {
                    "id": "cs_test_123",
                    "metadata": {
                        "order_id": str(self.order.id),
                        "cart_id": str(self.cart.id),
                    },
                    "amount_total": 3000,
                }
            }
        }

    def _handler(self):
        request = self.factory.post("/payments/webhook/")
        return StripeWH_Handler(request)

    @patch("payments.webhook_handler.send_order_confirmation_on_commit")
    def test_inventory_reduced_after_checkout_complete(self, mock_email):
        handler = self._handler()
        handler.handle_checkout_session_completed(self._event_payload())

        self.inventory.refresh_from_db()
        self.assertEqual(self.inventory.quantity, 7)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, Order.Status.PAID)

    @patch("payments.webhook_handler.send_order_confirmation_on_commit")
    def test_inventory_not_reduced_twice(self, mock_email):
        handler = self._handler()
        handler.handle_checkout_session_completed(self._event_payload())
        handler.handle_checkout_session_completed(self._event_payload())

        self.inventory.refresh_from_db()
        self.assertEqual(self.inventory.quantity, 7)

    @patch("payments.views.send_order_confirmation_now")
    @patch("payments.views.stripe.checkout.Session.retrieve")
    def test_success_view_reduces_inventory_when_transitioning(
        self, mock_retrieve, mock_email
    ):
        mock_retrieve.return_value = {
            "id": "cs_test_123",
            "metadata": {
                "order_id": str(self.order.id),
                "cart_id": str(self.cart.id),
            },
            "payment_status": "paid",
            "amount_total": 3000,
            "status": "complete",
            "payment_intent": "pi_1",
        }

        self.client.login(username="buyer", password="pw")
        resp = self.client.get(
            reverse("payments:success"),
            {"session_id": "cs_test_123"},
        )
        self.assertEqual(resp.status_code, 200)
        self.inventory.refresh_from_db()
        self.assertEqual(self.inventory.quantity, 7)
