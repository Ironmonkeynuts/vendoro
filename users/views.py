from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render, redirect

from .models import BuyerProfile
from .forms import UserNameForm, BuyerProfileForm


@login_required
def profile(request):
    """
    Profile page: lets a user edit their account name and default addresses.
    Ensures a BuyerProfile exists. Saves both forms atomically.
    """
    profile, _ = BuyerProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        uform = UserNameForm(request.POST, instance=request.user)
        pform = BuyerProfileForm(request.POST, instance=profile)

        if uform.is_valid() and pform.is_valid():
            with transaction.atomic():
                uform.save()
                pform.save()
            messages.success(request, "Your profile has been updated.")
            return redirect("users:profile")

        messages.error(request, "Please correct the errors below.")
    else:
        uform = UserNameForm(instance=request.user)
        pform = BuyerProfileForm(instance=profile)

    return render(
        request,
        "users/profile.html",
        {"uform": uform, "pform": pform},
    )
