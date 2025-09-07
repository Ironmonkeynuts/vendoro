# apps/marketplace/forms.py
from django import forms
from django.core.exceptions import ValidationError
from .models import Product, Shop


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
    """Form for creating and updating shops."""
    class Meta:
        model = Shop
        fields = ["name", "tagline", "primary_color", "highlight_color"]
        widgets = {
            "primary_color": forms.TextInput(attrs={"type": "color"}),
            "highlight_color": forms.TextInput(attrs={"type": "color"}),
        }
