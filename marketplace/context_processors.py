import os
import cloudinary as cld
from django.conf import settings


def cloudinary(request):
    """
    Expose Cloudinary cloud name + API key for the front-end widget.
    Pull from runtime SDK first, then env, then settings;
    always strip whitespace.
    """
    cfg = cld.config()
    store = getattr(settings, "CLOUDINARY_STORAGE", {})

    cloud_name = (
        (cfg.cloud_name or "") 
        or os.environ.get("CLOUDINARY_NAME", "") 
        or store.get("CLOUD_NAME", "")
    ).strip()

    api_key = (
        (cfg.api_key or "")
        or os.environ.get("CLOUDINARY_API", "")         # your current env var name
        or os.environ.get("CLOUDINARY_API_KEY", "")     # also support the standard name
        or store.get("API_KEY", "")
    ).strip()

    return {
        "CLOUDINARY_CLOUD_NAME": cloud_name,
        "CLOUDINARY_API_KEY": api_key,
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
