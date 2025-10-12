from django import forms


class NewsletterForm(forms.Form):
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={
            "class": "form-control",
            "placeholder": "you@example.com"
        }),
    )
    agree = forms.BooleanField(
        label="I agree to receive the Vendoro newsletter",
        required=True,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )
    # Honeypot
    website = forms.CharField(required=False, widget=forms.TextInput(attrs={
        "autocomplete": "off",
        "class": "d-none",
        "tabindex": "-1",
        "aria-hidden": "true",
    }))
