from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from .models import Cart

@receiver(user_logged_in)
def merge_guest_cart(sender, user, request, **kwargs):
    skey = request.session.session_key
    if not skey:
        return

    guest_cart = Cart.objects.filter(
        user__isnull=True, session_key=skey, active=True
    ).first()
    if not guest_cart:
        return

    user_cart, _ = Cart.objects.get_or_create(user=user, active=True)

    for g_item in guest_cart.items.all():
        u_item, created = user_cart.items.get_or_create(product=g_item.product)
        if created:
            u_item.quantity = g_item.quantity
        else:
            u_item.quantity += g_item.quantity
        u_item.save()

    guest_cart.delete()
