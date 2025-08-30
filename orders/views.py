from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from marketplace.models import Product
from .models import Cart, CartItem
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
def add_to_cart(request, product_id):
    if request.method != "POST":
        return HttpResponseBadRequest("POST required")
    form = QuantityAddForm(request.POST)
    if not form.is_valid():
        return HttpResponseBadRequest("Invalid quantity")
    qty = form.cleaned_data["quantity"]
    product = get_object_or_404(Product, id=product_id, is_active=True)
    cart = get_active_cart(request.user)
    item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if created:
        item.quantity = qty
    else:
        item.quantity += qty
    item.save()
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({
            "ok": True,
            "qty": item.quantity,
            "total": float(cart.total())
        })
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
    return JsonResponse({
        "ok": True,
        "total": float(cart.total())
    })
