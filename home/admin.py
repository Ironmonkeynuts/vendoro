from django.contrib import admin
from .models import NewsletterSubscription


@admin.register(NewsletterSubscription)
class NewsletterSubscriptionAdmin(admin.ModelAdmin):
    list_display = ("email", "is_active", "user", "created_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("email", "user__username", "user__email")
