from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from home.views import index
from allauth.account.decorators import verified_email_required
from django.http import HttpResponse


@verified_email_required
def verified(_):
    return HttpResponse("Verified area ✔")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("protected/", verified, name="verified"),
    path("", index, name="home"),
    path("home/", index, name="home_alt"),
    path(
        "browse/",
        include(
            ("marketplace.urls", "marketplace"),
            namespace="marketplace"
        )
    ),
    path(
        "orders/",
        include(
            ("orders.urls", "orders"),
            namespace="orders"
        )
    ),
    path(
        "payments/",
        include(
            ("payments.urls", "payments"),
            namespace="payments"
        )
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
