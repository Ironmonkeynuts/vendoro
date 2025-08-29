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


admin.site.register(Order)
admin.site.register(OrderItem)
