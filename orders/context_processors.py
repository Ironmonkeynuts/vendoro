from django.db.models import Sum
from .models import Cart


def cart_count(request):
    """
    Count the number of items in the user's cart.
    """
    if not request.user.is_authenticated:
        return {"cart_count": 0}
    cart = (Cart.objects
                .filter(user=request.user, active=True)
                .only("id")
                .order_by("-id")
                .first())
    if not cart:
        return {"cart_count": 0}
    total = cart.items.aggregate(c=Sum("quantity"))["c"] or 0
    return {"cart_count": total}
