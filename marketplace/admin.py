from django.contrib import admin
from .models import (
    Shop,
    Category,
    Product,
    ProductImage,
    Inventory
)


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "slug")
    # Prevent editing slug in admin
    readonly_fields = ("slug",)


admin.site.register(Category)
admin.site.register(Product)
admin.site.register(ProductImage)
admin.site.register(Inventory)
