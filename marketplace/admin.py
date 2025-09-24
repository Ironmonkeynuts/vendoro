from django.contrib import admin
from .models import (
    Shop,
    Category,
    Product,
    ProductImage,
    Inventory,
    ProductReview
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


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "user", "rating", "created_at")
    list_filter = ("rating", "created_at", "product__shop")
    search_fields = ("product__title", "user__username", "comment")
