from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinLengthValidator


class User(AbstractUser):
    """ Custom user model """
    # Define user types
    class UserType(models.TextChoices):
        BUYER = "buyer", _("Buyer")
        SELLER = "seller", _("Seller")
    user_type = models.CharField(
        max_length=10, choices=UserType.choices, blank=True, null=True
        )

    def is_buyer(self):
        return self.user_type == self.UserType.BUYER

    def is_seller(self):
        return self.user_type == self.UserType.SELLER

    def __str__(self):
        return f"{self.username} ({self.user_type or 'guest/admin'})"


class BuyerProfile(models.Model):
    user = models.OneToOneField(
        'users.User', on_delete=models.CASCADE, related_name='buyer_profile'
    )
    display_name = models.CharField(max_length=120, blank=True)
    default_shipping_email = models.EmailField(max_length=255, blank=True)
    default_shipping_telephone = models.CharField(max_length=20, blank=True)
    default_shipping_address1 = models.TextField(max_length=255, blank=True)
    default_shipping_address2 = models.TextField(max_length=255, blank=True)
    default_shipping_city = models.CharField(max_length=120, blank=True)
    default_shipping_postcode = models.CharField(max_length=20, blank=True)
    default_shipping_country = models.CharField(max_length=120, blank=True)
    marketing_opt_in = models.BooleanField(default=False)


class SellerProfile(models.Model):
    user = models.OneToOneField(
        'users.User', on_delete=models.CASCADE, related_name='seller_profile'
    )
    legal_name = models.CharField(max_length=200)
    tax_id = models.CharField(
        max_length=20, blank=True, validators=[MinLengthValidator(10)]
    )
    contact_email = models.EmailField(max_length=255, blank=True)
    contact_telephone = models.CharField(max_length=20, blank=True)
