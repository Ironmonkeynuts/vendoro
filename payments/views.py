from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest
from django.shortcuts import redirect, render
from django.urls import reverse
from decimal import Decimal
from orders.models import Cart, Order, OrderItem
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY


def _abs_url(request, name):
    return request.build_absolute_uri(reverse(name))


def _pence(amount: Decimal) -> int:
    return int(Decimal(amount) * 100)


@login_required
def create_checkout_session(request):
    if request.method != "POST":
        return HttpResponseBadRequest("POST required")

    cart = Cart.objects.filter(
        user=request.user, active=True
    ).prefetch_related("items__product", "items").first()
    if not cart or cart.items.count() == 0:
        messages.error(request, "Your cart is empty.")
        return redirect("orders:cart_detail")
    # Enforce single-shop cart for now
    shops = {i.product.shop_id for i in cart.items.all()}
    if len(shops) != 1:
        messages.error(
            request,
            "Multi‑shop checkout not yet supported. "
            "Please keep items from one shop."
        )
        return redirect("orders:cart_detail")

    shop_id = next(iter(shops))
    # Create pending Order + OrderItems (snapshot prices)
    total = Decimal("0.00")
    order = Order.objects.create(
        user=request.user, shop_id=shop_id, status=Order.Status.PENDING
    )
    for it in cart.items.all():
        OrderItem.objects.create(
            order=order,
            product=it.product,
            unit_price=it.product.price,
            quantity=it.quantity
        )
        total += it.product.price * it.quantity
    order.total_amount = total
    order.save()
    # Build Stripe line items
    line_items = []
    for it in cart.items.select_related("product"):
        line_items.append({
            "price_data": {
                "currency": settings.STRIPE_CURRENCY,
                "product_data": {"name": it.product.title},
                "unit_amount": _pence(it.product.price),
            },
            "quantity": it.quantity,
        })

    session = stripe.checkout.Session.create(
        mode="payment",
        line_items=line_items,
        success_url=_abs_url(request, "payments:success"),
        cancel_url=_abs_url(request, "payments:cancel"),
        metadata={
            "order_id": str(order.id),
            "user_id": str(request.user.id),
            "cart_id": str(cart.id),
        },
    )
    messages.info(request, "Redirecting to secure checkout…")
    # Redirect user to Stripe Checkout
    return redirect(session.url)

@login_required
def success(request):
    messages.success(request, "Payment received. Thank you! Your order is confirmed.")
    return render(request, "payments/success.html")


@login_required
def cancel(request):
    messages.warning(request, "Checkout canceled. Your cart is preserved.")
    return render(request, "payments/cancel.html")
