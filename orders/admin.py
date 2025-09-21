from django.contrib import admin
from .models import Cart, CartItem, Order, OrderItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "active", "created_at")
    list_filter = ("active",)
    inlines = [CartItemInline]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "shop",
        "status",
        "fulfillment_status",
        "total_amount",
        "created_at",
    )
    list_filter = ("status", "fulfillment_status", "shop")
    date_hierarchy = "created_at"


admin.site.register(OrderItem)
