from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """ Custom user model """
    # Define user types
    class UserType(models.TextChoices):
        BUYER = "buyer", _("Buyer")
        SELLER = "seller", _("Seller")
    user_type = models.CharField(max_length=10, choices=UserType.choices, blank=True, null=True)

    def is_buyer(self):
        return self.user_type == self.UserType.BUYER

    def is_seller(self):
        return self.user_type == self.UserType.SELLER

    def __str__(self):
        return f"{self.username} ({self.user_type or 'guest/admin'})"
