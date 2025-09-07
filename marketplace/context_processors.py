from django.conf import settings


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


def seller_nav(request):
    """
    Make the current user's shops available to the navbar on every page.
    Lightweight: only id/name/slug, and only when authenticated.
    """
    if not request.user.is_authenticated:
        return {}
    try:
        from .models import Shop
        shops = Shop.objects.filter(owner_id=request.user.id)\
                            .only("id", "name", "slug")[:20]
        return {"my_shops": shops}
    except Exception:
        # never break rendering if DB is unavailable
        return {"my_shops": []}
