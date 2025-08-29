from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, BuyerProfile, SellerProfile


@receiver(post_save, sender=User)
def create_profiles(sender, instance: User, created, **kwargs):
    if not created:
        return
    if instance.is_buyer():
        BuyerProfile.objects.get_or_create(user=instance)
    if instance.is_seller():
        SellerProfile.objects.get_or_create(
            user=instance,
            defaults={
                "legal_name": instance.get_full_name() or instance.username,
                "tax_id": "PENDING",
                "contact_email": instance.email or ""
            },
        )
