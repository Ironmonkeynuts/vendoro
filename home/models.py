from django.conf import settings
from django.db import models
import secrets


class NewsletterSubscription(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="newsletter_subscriptions",
    )
    email = models.EmailField(max_length=254, unique=True)
    is_active = models.BooleanField(max_length=64, default=True)
    # For future one-click unsubscribe / confirm links if you want them
    token = models.CharField(max_length=64, unique=True, editable=False,
                             default=secrets.token_hex)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.email} ({'active' if self.is_active else 'inactive'})"
