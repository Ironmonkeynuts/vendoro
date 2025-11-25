from django.db.models import Sum
from .models import Cart


def cart_count(request):
    """
    Count the number of items in the current cart
    (for either a logged-in user or a guest with a session).
    """
    # Logged-in user
    if request.user.is_authenticated:
        cart = (
            Cart.objects
            .filter(user=request.user, active=True)
            .order_by("-id")
            .only("id")
            .first()
        )
    else:
        # Guest: need an existing session key to have a cart
        session_key = request.session.session_key
        if not session_key:
            return {"cart_count": 0}

        cart = (
            Cart.objects
            .filter(user__isnull=True, session_key=session_key, active=True)
            .order_by("-id")
            .only("id")
            .first()
        )

    if not cart:
        return {"cart_count": 0}

    total = cart.items.aggregate(c=Sum("quantity"))["c"] or 0
    return {"cart_count": total}
