# orders/emails.py
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.db import transaction
from django.template.loader import render_to_string
import logging

logger = logging.getLogger(__name__)

def _render_order_confirmation(order):
    context = {"order": order, "user": order.user, "items": order.items.select_related("product")}
    subject = render_to_string("emails/order_confirmation_subject.txt", context).strip()
    text_body = render_to_string("emails/order_confirmation.txt", context)
    html_body = render_to_string("emails/order_confirmation.html", context)
    return subject, text_body, html_body

def send_order_confirmation_now(order):
    """Send immediately (no on_commit). Useful from the success page in dev."""
    if not order or not getattr(order.user, "email", ""):
        logger.info("No email sent: order or user email missing. order=%s", getattr(order, "id", None))
        return 0
    subject, text_body, html_body = _render_order_confirmation(order)
    msg = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", settings.EMAIL_HOST_USER),
        to=[order.user.email],
    )
    msg.attach_alternative(html_body, "text/html")
    sent = msg.send(fail_silently=False)
    logger.info("Order confirmation sent_now=%s to=%s order_id=%s", sent, order.user.email, order.id)
    return sent

def send_order_confirmation_on_commit(order):
    """Queue send after DB commit (good for webhooks and signals)."""
    def _send():
        try:
            send_order_confirmation_now(order)
        except Exception:
            logger.exception("Failed sending order confirmation (on_commit). order_id=%s", getattr(order, "id", None))
    transaction.on_commit(_send)
