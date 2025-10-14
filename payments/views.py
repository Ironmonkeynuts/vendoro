# payments/views.py
from decimal import Decimal
import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from orders.models import Cart, Order, OrderItem

import stripe

logger = logging.getLogger(__name__)
stripe.api_key = settings.STRIPE_SECRET_KEY


def _abs_url(request, name) -> str:
    return request.build_absolute_uri(reverse(name))


def _pence(amount: Decimal) -> int:
    # Convert Decimal pounds -> integer pence (no floats)
    return int((amount * 100).quantize(Decimal("1")))


@require_POST
@login_required
def create_checkout_session(request):
    # Ensure keys present
    if not settings.STRIPE_SECRET_KEY or not settings.STRIPE_PUBLIC_KEY:
        messages.error(
            request,
            "Payment is not configured. Please try again later."
        )
        return redirect("orders:cart_detail")

    cart = (
        Cart.objects
        .filter(user=request.user, active=True)
        .prefetch_related("items__product", "items__product__shop")
        .first()
    )
    if not cart or cart.items.count() == 0:
        messages.error(request, "Your cart is empty.")
        return redirect("orders:cart_detail")

    # Enforce single-shop cart
    shops = {i.product.shop_id for i in cart.items.all()}
    if len(shops) != 1:
        messages.error(
            request,
            (
                "Multi-shop checkout not yet supported. "
                "Please keep items from one shop."
            )
        )
        return redirect("orders:cart_detail")

    shop_id = next(iter(shops))

    # Create pending Order + snapshot items
    total = Decimal("0.00")
    order = Order.objects.create(
        user=request.user,
        shop_id=shop_id,
        status=Order.Status.PENDING
    )

    for it in cart.items.select_related("product"):
        OrderItem.objects.create(
            order=order,
            product=it.product,
            unit_price=it.product.price,
            quantity=it.quantity
        )
        total += it.product.price * it.quantity

    order.total_amount = total
    order.save(update_fields=["total_amount"])

    # Stripe line items
    line_items = [
        {
            "price_data": {
                "currency": settings.STRIPE_CURRENCY,
                "product_data": {"name": it.product.title},
                "unit_amount": _pence(it.product.price),
            },
            "quantity": it.quantity,
        }
        for it in cart.items.select_related("product")  # type: ignore
    ]

    try:
        session = stripe.checkout.Session.create(
            mode="payment",
            line_items=line_items,  # type: ignore
            success_url=(
                _abs_url(request, "payments:success")
                + "?session_id={CHECKOUT_SESSION_ID}"
            ),
            cancel_url=_abs_url(request, "payments:cancel"),
            customer_email=(request.user.email or None),
            metadata={
                "order_id": str(order.pk),
                "user_id": str(request.user.id),
                "cart_id": str(cart.pk),
            },
        )

        # Save the session id if your model has the field
        if hasattr(order, "stripe_checkout_session_id"):
            order.stripe_checkout_session_id = session.id
            order.save(update_fields=["stripe_checkout_session_id"])

        # 303 when redirecting to external origin is recommended
        return redirect(session.url, code=303)

    except stripe.AuthenticationError:
        order.status = Order.Status.CANCELED
        order.save(update_fields=["status"])
        messages.error(
            request,
            "Payment configuration error. Please try again later."
        )
        return redirect("orders:cart_detail")

    except stripe.StripeError as e:
        logger.exception("Stripe error creating Checkout Session")
        order.status = Order.Status.CANCELED
        order.save(update_fields=["status"])
        messages.error(
            request,
            getattr(e, "user_message", "Unable to start checkout.")
        )
        return redirect("orders:cart_detail")


@login_required
def success(request):
    session_id = request.GET.get("session_id")
    order = None

    if session_id:
        # Verify with Stripe (helpful UX, webhook is still the source of truth)
        try:
            session = stripe.checkout.Session.retrieve(session_id)
        except stripe.StripeError:
            session = None

        if session:
            # Find order by session id or metadata
            order = (
                Order.objects.filter(
                    stripe_checkout_session_id=session.id
                ).first()
                or Order.objects.filter(
                    id=session.get("metadata", {}).get("order_id")
                ).first()
            )

            # Idempotently mark as paid if Stripe says it’s paid
            if (
                order
                and (
                    session.get("status") == "complete"
                    or session.get("payment_status") == "paid"
                )
            ):
                changed = False
                if order.status != Order.Status.PAID:
                    order.status = Order.Status.PAID
                    changed = True
                if session.get("amount_total") is not None:
                    reported = Decimal(
                        (session["amount_total"]) / Decimal("100")
                    )
                    if reported != order.total_amount:
                        logger.warning(
                            "Stripe amount mismatch on success page",
                            extra={
                                "order_id": order.pk,
                                "expected": str(order.total_amount),
                                "reported": str(reported),
                            },
                        )
                    order.total_amount = reported
                    changed = True
                if hasattr(order, "stripe_payment_intent"):
                    pi = session.get("payment_intent") or ""
                    if (
                        pi
                        and getattr(order, "stripe_payment_intent", "") != pi
                    ):
                        order.stripe_payment_intent = pi
                        changed = True
                if changed:
                    order.save()

            # Clear cart if present in metadata
            # (safe if already cleared by webhook)
            cart_id = session.get("metadata", {}).get("cart_id")
            if cart_id:
                try:
                    cart = Cart.objects.get(
                        id=cart_id,
                        user=request.user,
                        active=True
                    )
                    cart.items.all().delete()
                    cart.active = False
                    cart.save(update_fields=["active"])
                except Cart.DoesNotExist:
                    pass

    messages.success(
        request,
        "Payment received. Thank you! Your order is confirmed."
    )
    return render(request, "payments/success.html", {"order": order})


@login_required
def cancel(request):
    messages.warning(request, "Checkout canceled. Your cart is preserved.")
    return render(request, "payments/cancel.html")
