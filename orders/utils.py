from django.db import transaction
from .models import Cart


def get_active_cart(request, create=True):
    """
    Returns the active cart for:
      - authenticated users (by user)
      - guests (by session_key)

    If create=False, returns None instead of creating a new cart.
    Useful for navbar cart_count to avoid empty carts for random visitors.
    """
    if request.user.is_authenticated:
        with transaction.atomic():
            qs = (Cart.objects
                      .select_for_update()
                      .filter(user=request.user, active=True)
                      .order_by("-id"))
            cart = qs.first()
            if cart:
                qs.exclude(pk=cart.pk).update(active=False)
                return cart
            return (
                Cart.objects.create(user=request.user, active=True)
                if create
                else None
            )

    # Guest flow
    if not request.session.session_key:
        if not create:
            return None
        request.session.save()

    skey = request.session.session_key

    with transaction.atomic():
        qs = (Cart.objects
                  .select_for_update()
                  .filter(user__isnull=True, session_key=skey, active=True)
                  .order_by("-id"))
        cart = qs.first()
        if cart:
            qs.exclude(pk=cart.pk).update(active=False)
            return cart

        return (Cart.objects.create(
            user=None, session_key=skey, active=True
        ) if create else None)
