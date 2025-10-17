from __future__ import annotations
from decimal import Decimal
from typing import Tuple, List, Optional

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.db import transaction
from django.template.loader import render_to_string


def _load_order(order_or_id):
    """Return (order, items_list) with related objects preloaded."""
    from .models import Order  # local import to avoid circulars
    if isinstance(order_or_id, Order):
        order = order_or_id
    else:
        order = (
            Order.objects
            .select_related("user", "shop")
            .prefetch_related("items__product", "items__product__shop")
            .get(pk=order_or_id)
        )

    # Be robust to related_name:
    if hasattr(order, "items"):
        items_qs = order.items.select_related("product", "product__shop")
    else:
        # default reverse name if related_name wasn't set
        items_qs = order.orderitem_set.select_related("product", "product__shop")

    items = list(items_qs)
    return order, items


# orders/emails.py

def _render(order, items):
    """Render subject/text/html with a robust context."""
    placed_at = (
        getattr(order, "created_at", None)
        or getattr(order, "created", None)
        or getattr(order, "date_created", None)
    )
    status_display = (
        order.get_status_display() if hasattr(order, "get_status_display") else getattr(order, "status", "")
    )

    ctx = {
        "order": order,
        "items": items,
        "placed_at": placed_at,
        "status_display": status_display,
        "currency": getattr(settings, "CURRENCY_SYMBOL", "£"),
        # NEW: aliases so legacy templates using {{ user }} or {{ shop }} still work
        "user": getattr(order, "user", None),
        "shop": getattr(order, "shop", None),
    }

    subject = render_to_string("emails/order_confirmation_subject.txt", ctx).strip()
    text_body = render_to_string("emails/order_confirmation.txt", ctx)
    try:
        html_body = render_to_string("emails/order_confirmation.html", ctx)
    except Exception:
        html_body = None
    return subject, text_body, html_body


def send_order_confirmation_now(order_or_id, to_email: Optional[str] = None) -> bool:
    """Send the confirmation immediately with text + HTML. Returns True if sent."""
    order, items = _load_order(order_or_id)
    subject, text_body, html_body = _render(order, items)

    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", getattr(settings, "EMAIL_HOST_USER", None))
    to_email = to_email or getattr(getattr(order, "user", None), "email", None)
    if not (from_email and to_email):
        return False

    msg = EmailMultiAlternatives(subject, text_body, from_email, [to_email])
    if html_body:
        msg.attach_alternative(html_body, "text/html")
    msg.send(fail_silently=False)
    return True


def send_order_confirmation_on_commit(order_or_id) -> None:
    """Queue send until the current DB transaction commits."""
    transaction.on_commit(lambda: send_order_confirmation_now(order_or_id))
