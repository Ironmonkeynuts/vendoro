from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db import transaction
from django.db.models import F
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from marketplace.models import Product
from .models import CartItem, Order
from .forms import QuantityAddForm
from .utils import get_active_cart

# TEMPORARY ONLY — for validating email HTML
from django.http import HttpResponse
from django.template.loader import render_to_string


def email_debug_preview(request, order_id):
    """Super simple validator preview — NO tokens, NO auth."""
    order = Order.objects.get(id=order_id)
    html = render_to_string("emails/order_confirmation.html", {"order": order})
    return HttpResponse(html)


def cart_detail(request):
    cart = get_active_cart(request)
    items = cart.items.select_related("product")
    total = cart.total()
    return render(request, "orders/cart.html", {
        "cart": cart,
        "items": items,
        "total": total
    })


@require_POST
def add_to_cart(request, product_id):
    form = QuantityAddForm(request.POST)
    if not form.is_valid():
        return HttpResponseBadRequest("Invalid quantity")

    qty = max(1, min(form.cleaned_data["quantity"], 99))
    product = get_object_or_404(Product, id=product_id, is_active=True)

    with transaction.atomic():
        cart = get_active_cart(request)
        line, created = cart.items.get_or_create(
            product=product, defaults={"quantity": qty}
        )
        if not created:
            cart.items.filter(pk=line.pk).update(quantity=F("quantity") + qty)
            line.refresh_from_db(fields=["quantity"])

    messages.success(request, f"Added {qty} × {product.title} to your cart.")

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        total = str(cart.total())
        cart_count = sum(i.quantity for i in cart.items.all())
        return JsonResponse({
            "ok": True,
            "qty": line.quantity,
            "total": total,
            "cart_count": cart_count
        })

    return redirect("orders:cart_detail")


def update_quantity(request, item_id):
    if request.method != "POST":
        return HttpResponseBadRequest("POST required")
    try:
        qty = int(request.POST.get("quantity", "1"))
        if qty < 1:
            raise ValueError
    except ValueError:
        return HttpResponseBadRequest("Invalid quantity")

    cart = get_active_cart(request)
    item = get_object_or_404(
        CartItem, id=item_id, cart=cart, cart__active=True
    )

    item.quantity = qty
    item.save()
    return JsonResponse({
        "ok": True,
        "subtotal": float(item.subtotal()),
        "total": float(cart.total())
    })


def remove_item(request, item_id):
    if request.method != "POST":
        return HttpResponseBadRequest("POST required")

    cart = get_active_cart(request)
    item = get_object_or_404(
        CartItem, id=item_id, cart=cart, cart__active=True
    )

    qty = item.quantity
    title = item.product.title
    item.delete()

    messages.success(request, f"Removed {qty} × {title} from your cart.")
    return JsonResponse({
        "ok": True,
        "total": float(cart.total())
    })


def clear_cart(request):
    if request.method != "POST":
        return HttpResponseBadRequest("POST required")

    cart = get_active_cart(request)
    if cart:
        cart.items.all().delete()
        messages.success(request, "Your cart has been cleared.")
    return redirect("orders:cart_detail")


@login_required
def my_orders(request):
    orders = (
        Order.objects
        .filter(user=request.user)
        .select_related("shop")
        .prefetch_related("items__product__shop")
        .order_by("-id", "-created_at")
    )
    return render(request, "orders/my_orders.html", {"orders": orders})
