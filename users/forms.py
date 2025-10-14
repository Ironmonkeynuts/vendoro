from django import forms
from allauth.account.forms import SignupForm

from .models import User, BuyerProfile


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
        user.save(update_fields=["user_type"])
        return user


class UserNameForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name"]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control", "autocomplete": "given-name"}),
            "last_name": forms.TextInput(attrs={"class": "form-control", "autocomplete": "family-name"}),
        }

    def clean_first_name(self):
        v = (self.cleaned_data.get("first_name") or "").strip()
        return v

    def clean_last_name(self):
        v = (self.cleaned_data.get("last_name") or "").strip()
        return v


class BuyerProfileForm(forms.ModelForm):
    class Meta:
        model = BuyerProfile
        fields = [
            "display_name",
            # shipping
            "default_shipping_email",
            "default_shipping_telephone",
            "default_shipping_address1",
            "default_shipping_address2",
            "default_shipping_city",
            "default_shipping_postcode",
            "default_shipping_country",
            # billing
            "billing_same_as_shipping",
            "default_billing_email",
            "default_billing_telephone",
            "default_billing_address1",
            "default_billing_address2",
            "default_billing_city",
            "default_billing_postcode",
            "default_billing_country",
            # prefs
            "marketing_opt_in",
        ]
        widgets = {
            "display_name": forms.TextInput(attrs={"class": "form-control"}),

            "default_shipping_email": forms.EmailInput(attrs={"class": "form-control", "autocomplete": "email"}),
            "default_shipping_telephone": forms.TextInput(attrs={"class": "form-control", "autocomplete": "tel"}),
            "default_shipping_address1": forms.TextInput(attrs={"class": "form-control", "autocomplete": "address-line1"}),
            "default_shipping_address2": forms.TextInput(attrs={"class": "form-control", "autocomplete": "address-line2"}),
            "default_shipping_city": forms.TextInput(attrs={"class": "form-control", "autocomplete": "address-level2"}),
            "default_shipping_postcode": forms.TextInput(attrs={"class": "form-control", "autocomplete": "postal-code"}),
            "default_shipping_country": forms.TextInput(attrs={"class": "form-control", "autocomplete": "country"}),

            "billing_same_as_shipping": forms.CheckboxInput(attrs={"class": "form-check-input"}),

            "default_billing_email": forms.EmailInput(attrs={"class": "form-control", "autocomplete": "email"}),
            "default_billing_telephone": forms.TextInput(attrs={"class": "form-control", "autocomplete": "tel"}),
            "default_billing_address1": forms.TextInput(attrs={"class": "form-control", "autocomplete": "address-line1"}),
            "default_billing_address2": forms.TextInput(attrs={"class": "form-control", "autocomplete": "address-line2"}),
            "default_billing_city": forms.TextInput(attrs={"class": "form-control", "autocomplete": "address-level2"}),
            "default_billing_postcode": forms.TextInput(attrs={"class": "form-control", "autocomplete": "postal-code"}),
            "default_billing_country": forms.TextInput(attrs={"class": "form-control", "autocomplete": "country"}),

            "marketing_opt_in": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    # Normalize common fields (trim whitespace; lowercase emails)
    def _normalize(self, data: dict) -> dict:
        text_fields = [
            "display_name",
            "default_shipping_telephone",
            "default_shipping_address1",
            "default_shipping_address2",
            "default_shipping_city",
            "default_shipping_postcode",
            "default_shipping_country",
            "default_billing_telephone",
            "default_billing_address1",
            "default_billing_address2",
            "default_billing_city",
            "default_billing_postcode",
            "default_billing_country",
        ]
        for f in text_fields:
            if f in data and data[f] is not None:
                data[f] = data[f].strip()

        for f in ["default_shipping_email", "default_billing_email"]:
            if f in data and data[f]:
                data[f] = data[f].strip().lower()

        return data

    def clean(self):
        cleaned = self._normalize(super().clean())
        same = cleaned.get("billing_same_as_shipping")

        # If billing is different, ensure key address fields are provided
        if not same:
            required = [
                "default_billing_address1",
                "default_billing_city",
                "default_billing_postcode",
                "default_billing_country",
            ]
            for f in required:
                if not cleaned.get(f):
                    self.add_error(f, "This field is required when billing differs from shipping.")

        return cleaned

    def save(self, commit=True):
        obj = super().save(commit=False)

        # Mirror shipping -> billing when checkbox is ticked
        if self.cleaned_data.get("billing_same_as_shipping", True):
            obj.default_billing_email = self.cleaned_data.get("default_shipping_email", "") or ""
            obj.default_billing_telephone = self.cleaned_data.get("default_shipping_telephone", "") or ""
            obj.default_billing_address1 = self.cleaned_data.get("default_shipping_address1", "") or ""
            obj.default_billing_address2 = self.cleaned_data.get("default_shipping_address2", "") or ""
            obj.default_billing_city = self.cleaned_data.get("default_shipping_city", "") or ""
            obj.default_billing_postcode = self.cleaned_data.get("default_shipping_postcode", "") or ""
            obj.default_billing_country = self.cleaned_data.get("default_shipping_country", "") or ""

        if commit:
            obj.save()
        return obj
