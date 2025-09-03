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