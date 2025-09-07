from django.db import transaction
from .models import Cart


def get_active_cart(user):
    with transaction.atomic():
        qs = (Cart.objects
                  .select_for_update()
                  .filter(user=user, active=True)
                  .order_by('-id'))
        cart = qs.first()
        if cart:
            # Deactivate any other active carts
            qs.exclude(pk=cart.pk).update(active=False)
            return cart
        return Cart.objects.create(user=user, active=True)
