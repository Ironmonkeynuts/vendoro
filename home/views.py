from django import forms
from django.conf import settings
from django.core.mail import send_mail
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.html import strip_tags
from django.db import IntegrityError, DataError
from django.shortcuts import render, redirect
from .forms import NewsletterForm
from .models import NewsletterSubscription


def index(request):
    is_subscribed = False
    if request.user.is_authenticated:
        email = _normalized_email(request.user.email)
        if email:
            is_subscribed = NewsletterSubscription.objects.filter(
                email__iexact=email, is_active=True
            ).exists()

    return render(request, "home/index.html", {
        "newsletter_subscribed": is_subscribed,
    })


def error_404(request, exception):
    # Render your custom template; you can pass anything your base needs
    ctx = {"path": request.path}
    return render(request, "404.html", ctx, status=404)


class ContactForm(forms.Form):
    name = forms.CharField(
        max_length=120,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Your name"
            }
        )
    )
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "you@example.com"
            }
        )
    )
    subject = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Subject (optional)"
            }
        )
    )
    message = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 6,
                "placeholder": "How can we help?"
            }
        )
    )
    # simple honeypot
    website = forms.CharField(required=False, widget=forms.HiddenInput())


def contact(request):
    initial = {}
    if request.user.is_authenticated:
        initial["name"] = request.user.get_full_name() or request.user.username
        initial["email"] = request.user.email

    form = ContactForm(request.POST or None, initial=initial)

    if request.method == "POST" and form.is_valid():
        data = form.cleaned_data

        # Honeypot check
        if data.get("website"):
            messages.info(request, "Thanks! Message received.")
            return redirect("contact")

        subject = data["subject"].strip() or f"Contact form: {data['name']}"
        support_email = getattr(
            settings, "SUPPORT_EMAIL", settings.DEFAULT_FROM_EMAIL
        )

        context_bits = [
            f"From: {data['name']} <{data['email']}>",
            f"Subject: {subject}",
            "",
            strip_tags(data["message"]),
            "",
            f"Path: {request.path}",
            (
                "User: "
                f"{request.user.id if request.user.is_authenticated
                    else 'anonymous'}"
            ),
            f"UA: {request.META.get('HTTP_USER_AGENT', '-')}",
        ]
        body = "\n".join(context_bits)

        send_mail(
            subject=subject,
            message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[support_email],
            fail_silently=False,
        )

        messages.success(
            request,
            "Thanks! We’ve received your message and will be in touch shortly."
        )
        return redirect("contact")

    return render(request, "home/contact.html", {
        "form": form,
        "support_email": getattr(
            settings, "SUPPORT_EMAIL", settings.DEFAULT_FROM_EMAIL
        ),
    })


def _normalized_email(raw: str | None) -> str:
    return (raw or "").strip().lower()


def newsletter_subscribe(request):
    """
    Public endpoint to subscribe via the small form (home page).
    - Validates form + honeypot.
    - Normalizes email to lowercase.
    - Avoids duplicate rows by checking case-insensitively first.
    - Guards against DB length errors based on the model's max_length.
    """
    if request.method != "POST":
        return redirect("home")

    form = NewsletterForm(request.POST)
    if not form.is_valid():
        messages.error(
            request, "Please enter a valid email and accept the checkbox."
        )
        return redirect("home")

    # Honeypot: if filled, silently ignore bots.
    if form.cleaned_data.get("website"):
        return redirect("home")

    email = _normalized_email(form.cleaned_data["email"])

    # Respect the model's configured length to prevent DataError
    email_field = NewsletterSubscription._meta.get_field("email")
    max_len = getattr(email_field, "max_length", 254) or 254
    if len(email) > max_len:
        messages.error(
            request,
            (
                f"That email address is too long. Please use one shorter than "
                f"{max_len} characters."
            ),
        )
        return redirect("home")

    # Find existing subscription case-insensitively first
    sub = (
        NewsletterSubscription.objects
        .filter(email__iexact=email)
        .first()
    )

    try:
        if sub:
            # Reactivate / attach user if needed
            changed_fields = []
            if not sub.is_active:
                sub.is_active = True
                changed_fields.append("is_active")
            if request.user.is_authenticated and not sub.user_id:
                sub.user = request.user
                changed_fields.append("user")
            if changed_fields:
                sub.save(update_fields=changed_fields)
        else:
            # Create fresh subscription
            NewsletterSubscription.objects.create(
                email=email,
                user=request.user if request.user.is_authenticated else None,
                is_active=True,
            )

    except (IntegrityError, DataError):
        # Safety net: resolve races or unexpected constraints
        existing = (
            NewsletterSubscription.objects.filter(email__iexact=email).first()
        )
        if existing:
            if not existing.is_active:
                existing.is_active = True
                existing.save(update_fields=["is_active"])
        else:
            messages.error(
                request,
                (
                    "We couldn’t save your subscription right now. "
                    "Please try again."
                ),
            )
            return redirect("home")

    messages.success(request, "Thanks! You’re subscribed to the Vendoro newsletter.")
    return redirect("home")


@login_required
def newsletter_manage(request):
    """
    Authenticated page to manage the current user's newsletter status.
    POST expects action=subscribe|unsubscribe.
    """
    email = _normalized_email(getattr(request.user, "email", ""))
    sub = (
        NewsletterSubscription.objects.filter(email__iexact=email).first()
        if email else None
    )

    if request.method == "POST":
        action = (request.POST.get("action") or "").strip().lower()

        if action == "subscribe":
            if not email:
                messages.error(
                    request,
                    (
                        "Your account has no email address. "
                        "Add one to your profile to subscribe."
                    ),
                )
                return redirect("newsletter_manage")

            email_field = NewsletterSubscription._meta.get_field("email")
            max_len = getattr(email_field, "max_length", 254) or 254
            if len(email) > max_len:
                messages.error(
                    request,
                    (
                        f"Your account email is longer than the allowed "
                        f"{max_len} characters."
                    ),
                )
                return redirect("newsletter_manage")

            try:
                if sub:
                    changed = False
                    if not sub.is_active:
                        sub.is_active = True
                        changed = True
                    if not sub.user_id:
                        sub.user = request.user
                        changed = True
                    if changed:
                        sub.save(update_fields=["is_active", "user"])
                else:
                    # Create a subscription tied to the user’s email
                    NewsletterSubscription.objects.create(
                        user=request.user, email=email, is_active=True
                    )
                messages.success(request, "You’re subscribed.")
                return redirect("newsletter_manage")

            except IntegrityError:
                # Fix potential race/duplicate
                sub = (
                    NewsletterSubscription.objects
                    .filter(email__iexact=email)
                    .first()
                )
                if sub:
                    sub.is_active = True
                    if not sub.user_id:
                        sub.user = request.user
                    sub.save(update_fields=["is_active", "user"])
                    messages.success(request, "You’re subscribed.")
                    return redirect("newsletter_manage")
                messages.error(
                    request,
                    "Could not subscribe right now. Please try again."
                )
                return redirect("newsletter_manage")

            except DataError:
                messages.error(
                    request,
                    (
                        "We couldn’t save your subscription "
                        "due to an invalid value. "
                        "Please try again."
                    )
                )
                return redirect("newsletter_manage")

        elif action == "unsubscribe":
            if sub and sub.is_active:
                sub.is_active = False
                sub.save(update_fields=["is_active"])
                messages.success(request, "You’ve been unsubscribed.")
            else:
                messages.info(request, "You’re not currently subscribed.")
            return redirect("newsletter_manage")

        else:
            messages.error(request, "Unknown action.")
            return redirect("newsletter_manage")

    # GET: show current status
    context = {"email": email, "subscription": sub}
    return render(request, "home/newsletter_manage.html", context)
