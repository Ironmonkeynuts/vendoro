from django import forms
from allauth.account.forms import SignupForm
from .models import User


class RoleSignupForm(SignupForm):
    ROLE_CHOICES = [
        (User.UserType.BUYER, "Buyer"),
        (User.UserType.SELLER, "Seller"),
    ]
    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        label="Account type (Primary role)"
    )

    def save(self, request):
        user = super().save(request)
        user.user_type = self.cleaned_data["role"]
        user.save()
        return user
