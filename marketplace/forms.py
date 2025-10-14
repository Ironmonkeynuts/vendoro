# apps/marketplace/forms.py
from django import forms
from django.core.exceptions import ValidationError
from .models import Product, Shop, ProductReview, ReviewReply
from users.models import SellerProfile


class ProductForm(forms.ModelForm):
    """Form for creating and updating products."""
    def __init__(self, *args, shop=None, **kwargs):
        # Accept shop as a parameter to ensure title uniqueness within the shop
        self.shop = shop
        super().__init__(*args, **kwargs)

    class Meta:
        model = Product
        fields = ["title", "description", "category", "price", "is_active"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 6}),
        }

    def clean_title(self):
        # Validate that the product title is unique within the shop
        title = self.cleaned_data.get("title", "").strip()
        if not title:
            return title
        if not self.shop:
            # Editing case will have instance.shop; fallback to that
            self.shop = getattr(self.instance, "shop", None)
        if self.shop and Product.objects.filter(
            shop=self.shop, title=title
        ).exclude(pk=self.instance.pk).exists():
            raise ValidationError(
                "A product with this title already exists in this shop."
            )
        return title


class ShopForm(forms.ModelForm):
    """ Form for creating and updating shops. """
    def __init__(self, *args, owner=None, **kwargs):
        self.owner = owner
        super().__init__(*args, **kwargs)
        self.fields["name"].widget.attrs.update(
            {"placeholder": "My Awesome Shop"})

    class Meta:
        model = Shop
        fields = [
            "name", "tagline", "primary_color", "highlight_color",
            "legal_name_override", "tax_id_override", "contact_email_override",
            "contact_telephone_override", "banner"
        ]
        widgets = {
            "tagline": forms.TextInput(
                attrs={"placeholder": "Best products online!"}
            ),
            "primary_color": forms.TextInput(attrs={"type": "color"}),
            "highlight_color": forms.TextInput(attrs={"type": "color"}),
            "legal_name_override": forms.TextInput(
                attrs={"class": "form-control"}
            ),
            "tax_id_override": forms.TextInput(
                attrs={"class": "form-control"}
            ),
            "contact_email_override": forms.EmailInput(
                attrs={"class": "form-control"}
            ),
            "contact_telephone_override": forms.TextInput(
                attrs={"class": "form-control"}
            ),
        }

    def clean_name(self):
        name = (self.cleaned_data.get("name") or "").strip()
        owner = self.owner or getattr(self.instance, "owner", None)
        if owner and name and Shop.objects.filter(
            owner=owner, name__iexact=name
        ).exclude(pk=self.instance.pk).exists():
            raise ValidationError("You already have a shop with this name.")
        return name


class SellerProfileForm(forms.ModelForm):
    class Meta:
        model = SellerProfile
        fields = ["legal_name", "tax_id", "contact_email", "contact_telephone"]
        widgets = {
            "legal_name": forms.TextInput(attrs={"class": "form-control"}),
            "tax_id": forms.TextInput(attrs={"class": "form-control"}),
            "contact_email": forms.EmailInput(attrs={"class": "form-control"}),
            "contact_telephone": forms.TextInput(
                attrs={"class": "form-control"}
            ),
        }


class ProductReviewForm(forms.ModelForm):
    class Meta:
        model = ProductReview
        fields = ("rating", "comment")
        widgets = {
            "rating": forms.NumberInput(
                attrs={"min": 1, "max": 5, "step": 1, "class": "form-control"}
            ),
            "comment": forms.Textarea(
                attrs={"rows": 3, "class": "form-control"}
            ),
        }


class ReviewReplyForm(forms.ModelForm):
    class Meta:
        model = ReviewReply
        fields = ["body"]
        widgets = {
            "body": forms.Textarea(
                attrs={"rows": 2, "placeholder": "Write a reply..."}
            ),
        }
