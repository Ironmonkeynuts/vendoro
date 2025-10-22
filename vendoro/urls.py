from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.views.generic import RedirectView

# Build absolute static URLs for redirects:
from django.templatetags.static import static

from home import views as home_views
from home.views import index, contact
from allauth.account.decorators import verified_email_required

handler404 = "home.views.error_404"


@verified_email_required
def verified(_):
    return HttpResponse("Verified area ✔")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("account/", include(("users.urls", "users"), namespace="users")),
    path("protected/", verified, name="verified"),
    path("", index, name="home"),
    path("home/", index, name="home_alt"),
    path("contact/", contact, name="contact"),

    path(
        "browse/",
        include(
            ("marketplace.urls", "marketplace"),
            namespace="marketplace",
        ),
    ),
    path(
        "seller/",
        RedirectView.as_view(
            pattern_name="marketplace:seller",
            permanent=False,
        ),
        name="seller_redirect",
    ),
    path("orders/", include(("orders.urls", "orders"), namespace="orders")),
    path(
        "payments/",
        include(("payments.urls", "payments"), namespace="payments"),
    ),
    path(
        "control/",
        include(
            ("admintools.urls", "admintools"),
            namespace="admintools",
        ),
    ),
    path(
        "newsletter/",
        home_views.newsletter_manage,
        name="newsletter_manage",
    ),
    path(
        "newsletter/subscribe/",
        home_views.newsletter_subscribe,
        name="newsletter_subscribe",
    ),

    # Favicons / touch icons -> redirect to actual static assets
    path(
        "favicon.ico",
        RedirectView.as_view(
            url=static("favicon.ico"),
            permanent=True,
        ),
    ),
    path(
        "apple-touch-icon.png",
        RedirectView.as_view(
            url=static("img/vendoro-icon-180.png"),
            permanent=True,
        ),
    ),
]
