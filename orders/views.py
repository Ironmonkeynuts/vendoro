from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db import transaction
from django.db.models import F
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from marketplace.models import Product
from .models import Cart, CartItem, Order
from .forms import QuantityAddForm
from .utils import get_active_cart


@login_required
def cart_detail(request):
    cart, _ = Cart.objects.get_or_create(user=request.user, active=True)
    # cart.items is the reverse ForeignKey from CartItem model
    items = cart.items.select_related("product")
    total = cart.total()
    return render(request, "orders/cart.html", {
        "cart": cart,
        "items": items,
        "total": total
    })


@login_required
@require_POST  # Enforce POST method
def add_to_cart(request, product_id):
    form = QuantityAddForm(request.POST)
    if not form.is_valid():
        return HttpResponseBadRequest("Invalid quantity")

    # (optional) clamp to sane bounds
    qty = max(1, min(form.cleaned_data["quantity"], 99))

    product = get_object_or_404(Product, id=product_id, is_active=True)
    # Avoids double adds
    with transaction.atomic():
        # Locks the active cart row(s) in our utils
        cart = get_active_cart(request.user)
        # Create (qty=1) or fetch the line, then increment atomically with F()
        line, created = cart.items.get_or_create(
            product=product, defaults={"quantity": qty})
        if not created:
            cart.items.filter(pk=line.pk).update(quantity=F("quantity") + qty)
            # Refresh in-memory value if needed
            line.refresh_from_db(fields=["quantity"])

    messages.success(request, f"Added {qty} × {product.title} to your cart.")

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        # Safer to return strings for money/decimals
        total = str(cart.total())  
        # If you have a cart_count helper, compute it here too:
        cart_count = sum(i.quantity for i in cart.items.all())
        return JsonResponse({"ok": True, "qty": line.quantity, "total": total, "cart_count": cart_count})

    return redirect("orders:cart_detail")


@login_required
def update_quantity(request, item_id):
    if request.method != "POST":
        return HttpResponseBadRequest("POST required")
    try:
        qty = int(request.POST.get("quantity", "1"))
        if qty < 1:
            raise ValueError
    except ValueError:
        return HttpResponseBadRequest("Invalid quantity")

    item = get_object_or_404(
        CartItem, id=item_id, cart__user=request.user, cart__active=True)
    item.quantity = qty
    item.save()
    return JsonResponse({
        "ok": True,
        "subtotal": float(item.subtotal()),
        "total": float(item.cart.total())
    })


@login_required
def remove_item(request, item_id):
    if request.method != "POST":
        return HttpResponseBadRequest("POST required")
    item = get_object_or_404(
        CartItem,
        id=item_id,
        cart__user=request.user,
        cart__active=True
    )
    cart = item.cart
    item.delete()
    messages.success(
        request,
        f"Removed {item.quantity} × {item.product.title} from your cart."
    )
    return JsonResponse({
        "ok": True,
        "total": float(cart.total())
    })


@login_required
def clear_cart(request):
    if request.method != "POST":
        return HttpResponseBadRequest("POST required")
    cart = Cart.objects.filter(user=request.user, active=True).first()
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
