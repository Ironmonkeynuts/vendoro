from django.conf import settings
from .models import Cart


def cloudinary(request):
    """
    Make Cloudinary config available in
    templates for the front-end upload widget.
    """
    store = getattr(settings, "CLOUDINARY_STORAGE", {})
    return {
        "CLOUDINARY_CLOUD_NAME": store.get("CLOUD_NAME", ""),
        "CLOUDINARY_API_KEY": store.get("API_KEY", ""),
    }


def cart_count(request):
    """
    Count the number of items in the user's cart.
    """
    if not request.user.is_authenticated:
        return {"cart_count": 0}
    cart = Cart.objects.filter(user=request.user, active=True).first()
    count = sum((i.quantity for i in cart.items.all()), 0) if cart else 0
    return {"cart_count": count}
