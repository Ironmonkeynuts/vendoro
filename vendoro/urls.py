from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from django.urls import path, include, re_path
from django.views.defaults import page_not_found as django_page_not_found
from django.views.generic import RedirectView

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
            namespace="marketplace"
        )
    ),
    path(
        "seller/",
        RedirectView.as_view(
            pattern_name="marketplace:seller",
            permanent=False
        ),
        name="seller_redirect",
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
    path(
        "control/",
        include(
            ("admintools.urls", "admintools"),
            namespace="admintools"
        )
    ),
    path(
        "newsletter/",
        home_views.newsletter_manage,
        name="newsletter_manage"
    ),
    path(
        "newsletter/subscribe/",
        home_views.newsletter_subscribe,
        name="newsletter_subscribe"
    ),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )

    def dev_only_show_404(request):
        return django_page_not_found(
            request,
            Exception("dev"),
            template_name="404.html"
        )

    urlpatterns += [
        re_path(
            r"^__show404__$",
            dev_only_show_404,
            name="dev_show_404",
        ),
    ]
