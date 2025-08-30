from .models import Cart


def get_active_cart(user):
    return Cart.objects.get_or_create(user=user, active=True)[0]
