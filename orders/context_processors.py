from .models import Cart


def cart_count(request):
    if not request.user.is_authenticated:
        return {"cart_count": 0}
    cart = Cart.objects.filter(user=request.user, active=True).first()
    count = sum((i.quantity for i in cart.items.all()), 0) if cart else 0
    return {"cart_count": count}
