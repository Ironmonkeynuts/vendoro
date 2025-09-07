from django.conf import settings
from django.db import models
from django.db.models import (
    Q, CheckConstraint, UniqueConstraint,
    F, Sum, ExpressionWrapper, DecimalField
)
from django.core.validators import MinValueValidator
from decimal import Decimal, ROUND_HALF_UP
from marketplace.models import Product, Shop

User = settings.AUTH_USER_MODEL
TWO_DP = Decimal("0.01")


class Cart(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="carts"
    )
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user"],
                condition=Q(active=True),
                name="unique_active_cart_per_user",
            )
        ]
        indexes = [
            models.Index(fields=["user", "active"]),
        ]

    def total(self) -> Decimal:
        total = sum(
            (item.subtotal() for item in self.items.select_related("product")),
            Decimal("0.00")
        )
        return total.quantize(TWO_DP, rounding=ROUND_HALF_UP)

    def total_db(self) -> Decimal:
        expr = ExpressionWrapper(
            F("product__price") * F("quantity"),
            output_field=DecimalField(max_digits=12, decimal_places=2),
        )
        agg = self.items.aggregate(total=Sum(expr))
        return (agg["total"] or Decimal("0.00")).quantize(
            TWO_DP, rounding=ROUND_HALF_UP)

    def items_count(self) -> int:
        return self.items.aggregate(c=Sum("quantity"))["c"] or 0

    def __str__(self):
        return f"Cart #{self.id} for {self.user} (active={self.active})"


class CartItem(models.Model):
    cart = models.ForeignKey(
        "orders.Cart", on_delete=models.CASCADE, related_name="items"
    )
    product = models.ForeignKey(
        "marketplace.Product", on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField(
        default=1, validators=[MinValueValidator(1)]
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["cart", "product"], name="uniq_cart_product"
            ),
            CheckConstraint(
                check=Q(quantity__gte=1), name="cartitem_qty_gte_1"
            ),
        ]

    def subtotal(self) -> Decimal:
        return (self.product.price * self.quantity).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

    def __str__(self):
        return f"{self.quantity} × {self.product} (cart {self.cart_id})"


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PAID = "paid", "Paid"
        SHIPPED = "shipped", "Shipped"
        COMPLETED = "completed", "Completed"
        CANCELED = "canceled", "Canceled"

    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="orders"
    )
    shop = models.ForeignKey(
        Shop, on_delete=models.PROTECT, related_name="orders"
    )
    total_amount = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0.00")
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="items"
    )
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()

    def line_total(self):
        return (self.unit_price * self.quantity).quantize(
            TWO_DP, rounding=ROUND_HALF_UP)
