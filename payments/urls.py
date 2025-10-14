from django.urls import path
from . import views, webhooks

app_name = "payments"

urlpatterns = [
    path(
        "create-checkout-session/",
        views.create_checkout_session,
        name="create_checkout_session"
    ),
    path("success/", views.success, name="success"),
    path("cancel/", views.cancel, name="cancel"),
    path("stripe/webhook/", webhooks.webhook, name="stripe_webhook"),
]
