# apps/marketplace/forms.py
from django import forms
from .models import Product, Shop

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["title", "description", "category", "price", "is_active"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 6}),
        }

class ShopForm(forms.ModelForm):
    class Meta:
        model = Shop
        fields = ["name", "tagline", "primary_color", "highlight_color"]
        widgets = {
            "primary_color": forms.TextInput(attrs={"type": "color"}),
            "highlight_color": forms.TextInput(attrs={"type": "color"}),
        }
