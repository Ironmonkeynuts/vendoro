from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from decimal import Decimal
from orders.models import Cart, Order, OrderItem
import stripe
import logging

stripe.api_key = settings.STRIPE_SECRET_KEY

logger = logging.getLogger(__name__)


def _abs_url(request, name):
    return request.build_absolute_uri(reverse(name))


def _pence(amount: Decimal) -> int:
    return int(Decimal(amount) * 100)


@login_required
def create_checkout_session(request):
    if request.method != "POST":
        return HttpResponseBadRequest("POST required")

    # Fast fail if keys aren’t set
    if not settings.STRIPE_SECRET_KEY or not settings.STRIPE_PUBLIC_KEY:
        messages.error(
            request, "Payment is not configured. Please try again later."
        )
        return redirect("orders:cart_detail")

    cart = (Cart.objects
            .filter(user=request.user, active=True)
            .prefetch_related("items__product", "items")
            .first())
    if not cart or cart.items.count() == 0:
        messages.error(request, "Your cart is empty.")
        return redirect("orders:cart_detail")

    # Enforce single-shop cart (for now)
    shops = {i.product.shop_id for i in cart.items.all()}
    if len(shops) != 1:
        messages.error(
            request,
            "Multi-shop checkout not yet supported. "
            "Please keep items from one shop."
        )
        return redirect("orders:cart_detail")

    shop_id = next(iter(shops))

    # Create pending Order + snapshot items
    total = Decimal("0.00")
    order = Order.objects.create(
        user=request.user, shop_id=shop_id, status=Order.Status.PENDING
    )
    for it in cart.items.all():
        OrderItem.objects.create(
            order=order, product=it.product, unit_price=it.product.price,
            quantity=it.quantity
        )
        total += it.product.price * it.quantity
    order.total_amount = total
    order.save()

    line_items = [{
        "price_data": {
            "currency": settings.STRIPE_CURRENCY,
            "product_data": {"name": it.product.title},
            "unit_amount": _pence(it.product.price),
        },
        "quantity": it.quantity,
    } for it in cart.items.select_related("product")]  # type: ignore

    try:
        session = stripe.checkout.Session.create(
            mode="payment",
            line_items=line_items,  # type: ignore
            success_url=_abs_url(request, "payments:success"),
            cancel_url=_abs_url(request, "payments:cancel"),
            metadata={  # type: ignore
                "order_id": str(order.id),
                "user_id": str(request.user.id),
                "cart_id": str(cart.id)
            },
        )
        return redirect(session.url)

    except stripe.AuthenticationError:
        order.status = Order.Status.CANCELED
        order.save()
        messages.error(
            request,
            "Payment configuration error. Please try again later."
        )
        return redirect("orders:cart_detail")

    except stripe.StripeError as e:
        order.status = Order.Status.CANCELED
        order.save()
        messages.error(
            request,
            getattr(e, "user_message", "Unable to start checkout.")
        )
        return redirect("orders:cart_detail")


@login_required
def success(request):
    messages.success(
        request,
        "Payment received. Thank you! Your order is confirmed."
    )
    return render(request, "payments/success.html")


@login_required
def cancel(request):
    messages.warning(request, "Checkout canceled. Your cart is preserved.")
    return render(request, "payments/cancel.html")


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError:
        return HttpResponse(status=400)
    except stripe.SignatureVerificationError:
        return HttpResponse(status=400)

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        metadata = session.get("metadata", {})
        order_id = metadata.get("order_id")
        cart_id = metadata.get("cart_id")

        if order_id:
            try:
                order = Order.objects.get(id=order_id)
                order.status = Order.Status.PAID
                if session.get("amount_total") is not None:
                    reported = Decimal(session["amount_total"]) / 100
                    if reported != order.total_amount:
                        logger.warning(
                            "Stripe amount mismatch",
                            extra={
                                "order_id": order.id,  # type: ignore
                                "expected": str(order.total_amount),
                                "reported": str(reported)
                            }
                        )
                    order.total_amount = reported
                order.save()
            except Order.DoesNotExist:
                pass

        if cart_id:
            try:
                cart = Cart.objects.get(id=cart_id)
                cart.items.all().delete()  # type: ignore
                cart.active = False
                cart.save()
            except Cart.DoesNotExist:
                pass

    return HttpResponse(status=200)
