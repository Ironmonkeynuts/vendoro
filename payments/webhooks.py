# payments/webhooks.py
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from payments.webhook_handler import StripeWH_Handler

import stripe
from stripe import SignatureVerificationError
import logging

logger = logging.getLogger(__name__)

@require_POST
@csrf_exempt
def webhook(request):
    """Listen for webhooks from Stripe (safe & chatty)."""
    # Accept both env var names to avoid mismatches
    wh_secret = (
        getattr(settings, "STRIPE_WH_SECRET", None)
        or getattr(settings, "STRIPE_WEBHOOK_SECRET", None)
    )
    if not wh_secret:
        logger.error("Stripe webhook error: no signing secret set (STRIPE_WH_SECRET / STRIPE_WEBHOOK_SECRET).")
        return HttpResponse("Server misconfigured", status=500)

    # Not strictly required for verification, but fine to set
    stripe.api_key = getattr(settings, "STRIPE_SECRET_KEY", "")

    payload = request.body  # bytes
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, wh_secret)
    except ValueError as e:
        logger.warning("Webhook invalid payload: %s", e, exc_info=True)
        return HttpResponse("Invalid payload", status=400)
    except SignatureVerificationError as e:
        logger.warning("Webhook invalid signature: %s", e)
        return HttpResponse("Invalid signature", status=400)
    except Exception as e:
        logger.exception("Webhook verification error")
        return HttpResponse("Webhook error", status=400)

    evt_type = event.get("type")
    evt_id = event.get("id")
    logger.info("Stripe webhook received id=%s type=%s", evt_id, evt_type)

    handler = StripeWH_Handler(request)

    # Map the events you actually handle; everything else falls back to generic 200
    event_map = {
        "checkout.session.completed": handler.handle_checkout_session_completed,
        "payment_intent.succeeded": handler.handle_payment_intent_succeeded,
        "payment_intent.payment_failed": handler.handle_payment_intent_payment_failed,
    }

    event_handler = event_map.get(evt_type, handler.handle_event)

    try:
        return event_handler(event)
    except Exception:
        # Never bubble exceptions to Stripe; log and return 200 so Stripe doesn't keep retrying forever
        logger.exception("Exception while handling webhook type=%s id=%s", evt_type, evt_id)
        return HttpResponse("Handled with internal error (see logs)", status=200)
