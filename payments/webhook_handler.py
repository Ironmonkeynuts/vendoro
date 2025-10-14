# payments/webhook_handler.py
from django.http import HttpResponse
from decimal import Decimal
import logging

from orders.models import Order, Cart

logger = logging.getLogger(__name__)


class StripeWH_Handler:
    """Handle Stripe webhooks safely."""

    def __init__(self, request):
        self.request = request

    def handle_event(self, event):
        """Default handler for uninteresting/unknown events."""
        logger.info("Unhandled Stripe event: %s", event.get("type"))
        return HttpResponse(f"Unhandled event {event.get('type')}", status=200)

    # --- If you also care about raw PaymentIntent events, keep these: ---
    def handle_payment_intent_succeeded(self, event):
        logger.info("payment_intent.succeeded received (noop).")
        return HttpResponse("OK", status=200)

    def handle_payment_intent_payment_failed(self, event):
        logger.info("payment_intent.payment_failed received (noop).")
        return HttpResponse("OK", status=200)

    # --- Main one for Stripe Checkout: ---
    def handle_checkout_session_completed(self, event):
        """Mark order paid & clear cart (idempotent)."""
        session = event["data"]["object"]
        metadata = session.get("metadata") or {}
        order_id = metadata.get("order_id")
        cart_id = metadata.get("cart_id")

        logger.info(
            "checkout.session.completed: session_id=%s order_id=%s cart_id=%s",
            session.get("id"), order_id, cart_id
        )

        # Update order (idempotent)
        if order_id:
            try:
                order = Order.objects.get(id=order_id)
                # Only transition forward
                if order.status != Order.Status.PAID:
                    order.status = Order.Status.PAID
                # Trust Stripe total if present
                if session.get("amount_total") is not None:
                    reported = Decimal(session["amount_total"]) / Decimal("100")
                    if reported != order.total_amount:
                        logger.warning(
                            "Stripe total mismatch for order %s: expected=%s "
                            "reported=%s",
                            order.pk, order.total_amount, reported
                        )
                    order.total_amount = reported
                # Store session / payment intent if your model has fields
                if hasattr(order, "stripe_checkout_session_id"):
                    order.stripe_checkout_session_id = session.get("id", "")
                if hasattr(order, "stripe_payment_intent"):
                    order.stripe_payment_intent = session.get("payment_intent", "") or getattr(order, "stripe_payment_intent", "")
                order.save()
            except Order.DoesNotExist:
                logger.warning("Webhook: order %s not found", order_id)

        # Clear cart (idempotent)
        if cart_id:
            try:
                cart = Cart.objects.get(id=cart_id)
                cart.items.all().delete()
                cart.active = False
                cart.save(update_fields=["active"])
            except Cart.DoesNotExist:
                logger.info("Webhook: cart %s not found (already cleared?)", cart_id)

        return HttpResponse("OK", status=200)
