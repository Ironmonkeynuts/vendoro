from django.contrib import admin
from .models import Cart, CartItem, Order, OrderItem, FulfillmentStatus


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "active", "created_at")
    list_filter = ("active",)
    inlines = [CartItemInline]


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    can_delete = False
    readonly_fields = ("product", "quantity", "unit_price", "line_total")
    fields = ("product", "quantity", "unit_price", "line_total")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    # Shown as columns on the list page
    list_display = (
        "id",
        "user",
        "status",
        "fulfillment_status",
        "total_amount",
        "created_at",
    )
    list_editable = ("status", "fulfillment_status")
    list_filter = ("status", "fulfillment_status", "created_at")
    search_fields = ("id", "user__username", "user__email")
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
    inlines = [OrderItemInline]

    # If these exist on your model, they’ll be readonly on the detail page
    readonly_fields = ("id", "created_at", "total_amount")

    # Bulk actions
    actions = [
        "mark_fulfillment_pending",
        "mark_fulfillment_processing",
        "mark_fulfillment_completed",
        "mark_status_pending",
        "mark_status_paid",
        "mark_status_canceled",
    ]

    # ---- Fulfillment actions ----
    def mark_fulfillment_pending(self, request, queryset):
        updated = queryset.update(fulfillment_status=FulfillmentStatus.PENDING)
        msg = f"Updated fulfillment to Pending on {updated} orders."
        self.message_user(request, msg)
    mark_fulfillment_pending.short_description = "Fulfillment → Pending"

    def mark_fulfillment_processing(self, request, queryset):
        updated = queryset.update(
            fulfillment_status=FulfillmentStatus.PROCESSING
        )
        self.message_user(
            request, f"Updated fulfillment to Processing on {updated} orders."
        )
    mark_fulfillment_processing.short_description = "Fulfillment → Processing"

    def mark_fulfillment_completed(self, request, queryset):
        updated = queryset.update(
            fulfillment_status=FulfillmentStatus.COMPLETED
        )
        self.message_user(
            request, f"Updated fulfillment to Completed on {updated} orders."
        )
    mark_fulfillment_completed.short_description = "Fulfillment → Completed"

    # ---- Order status actions (use your TextChoices) ----
    def mark_status_pending(self, request, queryset):
        updated = queryset.update(status=Order.Status.PENDING)
        self.message_user(
            request, f"Updated status to Pending on {updated} orders."
        )
    mark_status_pending.short_description = "Status → Pending"

    def mark_status_paid(self, request, queryset):
        updated = queryset.update(status=Order.Status.PAID)
        self.message_user(
            request, f"Updated status to Paid on {updated} orders."
        )
    mark_status_paid.short_description = "Status → Paid"

    def mark_status_canceled(self, request, queryset):
        updated = queryset.update(status=Order.Status.CANCELED)  # one 'L'
        self.message_user(
            request, f"Updated status to Canceled on {updated} orders."
        )
    mark_status_canceled.short_description = "Status → Canceled"


admin.site.register(OrderItem)
