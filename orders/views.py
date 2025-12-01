from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db import transaction
from django.db.models import F
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from marketplace.models import Product, Inventory
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
    items = cart.items.select_related("product", "product__inventory")
    total = cart.total()
    return render(request, "orders/cart.html", {
        "cart": cart,
        "items": items,
        "total": total
    })


def _get_stock_quantity(product):
    try:
        return product.inventory.quantity
    except Inventory.DoesNotExist:
        return None


@require_POST
def add_to_cart(request, product_id):
    form = QuantityAddForm(request.POST)
    if not form.is_valid():
        return HttpResponseBadRequest("Invalid quantity")

    qty = max(1, min(form.cleaned_data["quantity"], 99))
    product = get_object_or_404(
        Product.objects.select_related("inventory"),
        id=product_id,
        is_active=True
    )
    stock_limit = _get_stock_quantity(product)

    if stock_limit is not None and stock_limit < 1:
        msg = f"{product.title} is currently out of stock."
        messages.warning(request, msg)
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"ok": False, "error": msg}, status=400)
        return redirect("orders:cart_detail")

    with transaction.atomic():
        cart = get_active_cart(request)
        line = (
            cart.items
            .select_for_update()
            .select_related("product")
            .filter(product=product)
            .first()
        )
        existing_qty = line.quantity if line else 0

        available_to_add = None
        if stock_limit is not None:
            available_to_add = max(0, stock_limit - existing_qty)

        if available_to_add is not None and available_to_add <= 0:
            msg = (
                f"You already have all available stock of {product.title} "
                "in your cart."
            )
            messages.info(request, msg)
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse(
                    {"ok": False, "error": msg, "qty": existing_qty},
                    status=400
                )
            return redirect("orders:cart_detail")

        qty_to_add = qty if available_to_add is None else min(qty, available_to_add)

        if line:
            cart.items.filter(pk=line.pk).update(
                quantity=F("quantity") + qty_to_add
            )
            line.refresh_from_db(fields=["quantity"])
        else:
            line = cart.items.create(
                product=product,
                quantity=qty_to_add,
            )

    added_qty = qty_to_add
    if stock_limit is not None and added_qty < qty:
        messages.info(
            request,
            f"Only {stock_limit} × {product.title} available. "
            f"Added the remaining {added_qty}."
        )
    else:
        messages.success(request, f"Added {added_qty} × {product.title} to your cart.")

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        total = str(cart.total())
        cart_count = sum(i.quantity for i in cart.items.all())
        return JsonResponse({
            "ok": True,
            "qty": line.quantity,
            "added": added_qty,
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

    try:
        stock_limit = item.product.inventory.quantity
    except Inventory.DoesNotExist:
        stock_limit = None

    if stock_limit is not None:
        if stock_limit < 1:
            msg = f"{item.product.title} is currently out of stock."
            return JsonResponse(
                {"ok": False, "error": msg, "qty": item.quantity},
                status=400
            )
        if qty > stock_limit:
            qty = stock_limit
            warning = (
                f"Only {stock_limit} × {item.product.title} available. "
                "Quantity reduced to available stock."
            )
        else:
            warning = None
    else:
        warning = None

    item.quantity = qty
    item.save()
    response = {
        "ok": True,
        "qty": item.quantity,
        "subtotal": float(item.subtotal()),
        "total": float(cart.total())
    }
    if warning:
        response["warning"] = warning
    return JsonResponse(response)


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
