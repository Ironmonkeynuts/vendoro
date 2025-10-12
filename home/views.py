from django import forms
from django.conf import settings
from django.core.mail import send_mail
from django.contrib import messages
from django.utils.html import strip_tags
from django.shortcuts import render, redirect


def index(request):
    return render(request, "home/index.html")


def error_404(request, exception):
    # Render your custom template; you can pass anything your base needs
    ctx = {"path": request.path}
    return render(request, "404.html", ctx, status=404)


class ContactForm(forms.Form):
    name = forms.CharField(
        max_length=120,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Your name"})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "you@example.com"})
    )
    subject = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Subject (optional)"})
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 6, "placeholder": "How can we help?"})
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
            messages.info(request, "Thanks! Message received.")  # pretend success
            return redirect("contact")

        subject = data["subject"].strip() or f"Contact form: {data['name']}"
        support_email = getattr(settings, "SUPPORT_EMAIL", settings.DEFAULT_FROM_EMAIL)

        context_bits = [
            f"From: {data['name']} <{data['email']}>",
            f"Subject: {subject}",
            "",
            strip_tags(data["message"]),
            "",
            f"Path: {request.path}",
            f"User: {request.user.id if request.user.is_authenticated else 'anonymous'}",
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

        messages.success(request, "Thanks! We’ve received your message and will be in touch shortly.")
        return redirect("contact")

    return render(request, "home/contact.html", {
        "form": form,
        "support_email": getattr(settings, "SUPPORT_EMAIL", settings.DEFAULT_FROM_EMAIL),
    })
