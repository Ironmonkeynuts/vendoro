from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import (
    Q, F, Count, Avg, Sum, Prefetch, DecimalField, ExpressionWrapper
)
from django.db.models.functions import Coalesce
from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView, ListView
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.dateparse import parse_date
from decimal import Decimal
from datetime import datetime, time

from marketplace.models import Shop, Product, ProductReview
from orders.models import Order, OrderItem

User = get_user_model()


class SuperuserRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin for views that only superusers should access."""
    login_url = "account_login"

    def test_func(self):
        return self.request.user.is_superuser


class DashboardView(SuperuserRequiredMixin, TemplateView):
    """Admin dashboard home page."""
    template_name = "admintools/index.html"


class UserListView(SuperuserRequiredMixin, ListView):
    """List of users with search and sort functionality."""
    template_name = "admintools/users.html"
    model = User
    paginate_by = 25
    ordering = "-date_joined"

    SORT_MAP = {
        "username": "username",
        "-username": "-username",
        "email": "email",
        "-email": "-email",
        "date_joined": "date_joined",
        "-date_joined": "-date_joined",
        "is_staff": "is_staff",
        "-is_staff": "-is_staff",
        "is_active": "is_active",
        "-is_active": "-is_active",
    }

    def get_queryset(self):
        """Allow searching and sorting."""
        qs = super().get_queryset()
        q = self.request.GET.get("q", "").strip()
        if q:
            qs = qs.filter(
                Q(username__icontains=q) |
                Q(email__icontains=q) |
                Q(first_name__icontains=q) |
                Q(last_name__icontains=q)
            )
        sort = (self.request.GET.get("sort") or "").strip()
        order_by = self.SORT_MAP.get(sort, self.ordering)
        return qs.order_by(order_by)

    def get_context_data(self, **kwargs):
        """Add search and sort parameters to context."""
        ctx = super().get_context_data(**kwargs)
        ctx["q"] = (self.request.GET.get("q") or "").strip()
        ctx["sort"] = (self.request.GET.get("sort") or "").strip()
        return ctx


def _safe_redirect_next(request, fallback_name="admintools:users"):
    """
    Redirect back to ?next=... if it's a safe same-origin URL;
    otherwise fallback.
    """
    next_url = request.POST.get("next") or request.GET.get("next")
    if next_url and url_has_allowed_host_and_scheme(
        url=next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return redirect(next_url)
    return redirect(fallback_name)


@require_POST
def user_toggle_staff(request, pk: int):
    """Toggle staff status for a user."""
    # superuser-only (belt-and-suspenders)
    if not (request.user.is_authenticated and request.user.is_superuser):
        messages.error(request, "You do not have permission to do that.")
        return _safe_redirect_next(request)

    target = get_object_or_404(User, pk=pk)

    # Safety rails: don't edit other superusers; don't demote yourself
    if target.is_superuser and target != request.user:
        messages.error(
            request,
            "You cannot change staff status of another superuser."
        )
        return _safe_redirect_next(request)

    if target == request.user:
        messages.error(
            request,
            "You cannot change your own staff status here."
        )
        return _safe_redirect_next(request)

    target.is_staff = not target.is_staff
    target.save(update_fields=["is_staff"])
    messages.success(
        request,
        f"Set staff for {target.username} to "
        f"{'Yes' if target.is_staff else 'No'}."
    )
    return _safe_redirect_next(request)


@require_POST
def user_toggle_suspend(request, pk: int):
    """Toggle suspended (is_active) status for a user."""
    # superuser-only
    if not (request.user.is_authenticated and request.user.is_superuser):
        messages.error(request, "You do not have permission to do that.")
        return _safe_redirect_next(request)

    target = get_object_or_404(User, pk=pk)

    # Safety rails: don't suspend other superusers; don't suspend yourself
    if target.is_superuser and target != request.user:
        messages.error(request, "You cannot suspend another superuser.")
        return _safe_redirect_next(request)

    if target == request.user:
        messages.error(request, "You cannot suspend your own account.")
        return _safe_redirect_next(request)

    # "Suspend" = set is_active False; unsuspend = True
    target.is_active = not target.is_active
    target.save(update_fields=["is_active"])
    messages.success(
        request,
        f"{'Unsuspended' if target.is_active else 'Suspended'} "
        f"{target.username}."
    )
    return _safe_redirect_next(request)


@require_POST
def product_toggle_suspend(request, pk: int):
    """Superuser: toggle Product.is_active (suspend / activate)."""
    if not (request.user.is_authenticated and request.user.is_superuser):
        messages.error(request, "You do not have permission to do that.")
        return _safe_redirect_next(request, fallback_name="admintools:shops")

    product = get_object_or_404(
        Product.objects.select_related("shop", "shop__owner"),
        pk=pk
    )

    product.is_active = not product.is_active
    product.save(update_fields=["is_active"])

    messages.success(
        request,
        (
            f"{'Reactivated' if product.is_active else 'Suspended'} "
            f"“{product.title}”."
        )
    )
    return _safe_redirect_next(request, fallback_name="admintools:shops")


class ShopsProductsView(SuperuserRequiredMixin, TemplateView):
    """
    Admin-only page that lists all shops with expandable rows
    showing owner details and all products + per-product stats.
    """
    template_name = "admintools/shops_products.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        # Per-product stat annotations (efficiently reused via Prefetch)
        revenue_expr = ExpressionWrapper(
            F("orderitem__unit_price") * F("orderitem__quantity"),
            output_field=DecimalField(max_digits=12, decimal_places=2),
        )
        products_qs = (
            Product.objects.select_related("shop", "category")
            .annotate(
                review_count=Count("reviews", distinct=True),
                review_avg=Avg("reviews__rating"),
                items_sold=Sum("orderitem__quantity"),
                revenue=Sum(revenue_expr),
            )
            .order_by("title")
        )

        # Prefetch the annotated products to each shop as "adm_products"
        products_prefetch = Prefetch(
            "products", queryset=products_qs, to_attr="adm_products"
        )

        # Per-shop rollups
        shop_revenue_expr = ExpressionWrapper(
            F("products__orderitem__unit_price") *
            F("products__orderitem__quantity"),
            output_field=DecimalField(max_digits=12, decimal_places=2),
        )

        shops = (
            Shop.objects.select_related("owner")
            .prefetch_related(products_prefetch)
            .annotate(
                product_count=Count("products", distinct=True),
                total_reviews=Count("products__reviews", distinct=True),
                avg_rating=Avg("products__reviews__rating"),
                items_sold=Sum("products__orderitem__quantity"),
                gross_revenue=Sum(shop_revenue_expr),
            )
            .order_by("name")
        )

        ctx["shops"] = shops
        return ctx


class ReportsView(SuperuserRequiredMixin, TemplateView):
    """Site-wide reports dashboard (initial KPIs)."""
    template_name = "admintools/reports.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        # Users
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        suspended_users = total_users - active_users
        staff_users = User.objects.filter(is_staff=True).count()
        superusers = User.objects.filter(is_superuser=True).count()

        # Shops & Products
        total_shops = Shop.objects.count()
        total_products = Product.objects.count()
        active_products = Product.objects.filter(is_active=True).count()
        inactive_products = total_products - active_products

        # Orders & Revenue
        paid_orders = Order.objects.filter(status="paid")
        total_orders = paid_orders.count()

        # Revenue = sum of qty * unit_price from paid orders
        line_amount_expr = ExpressionWrapper(
            F("quantity") * F("unit_price"),
            output_field=OrderItem._meta.get_field("unit_price")
        )
        gross_revenue = (
            OrderItem.objects.filter(order__status="paid")
            .aggregate(total=Coalesce(Sum(line_amount_expr), Decimal("0")))
        )["total"] or Decimal("0")

        # Range parsing
        now = timezone.now()
        rng = (self.request.GET.get("range") or "7").strip()
        start_param = self.request.GET.get("start")
        end_param = self.request.GET.get("end")

        if rng in {"7", "30", "90"}:
            start = now - timezone.timedelta(days=int(rng))
            end = now
            range_label = rng
        else:
            # custom
            sd = parse_date(start_param) if start_param else None
            ed = parse_date(end_param) if end_param else None
            start = timezone.make_aware(
                datetime.combine(sd, time.min)
            ) if sd else now - timezone.timedelta(days=7)
            end = timezone.make_aware(
                datetime.combine(ed, time.max)
            ) if ed else now
            range_label = "custom"

        ctx["range"] = {"label": range_label, "start": start, "end": end}

        # Recent windows (fixed)
        last_7_days = now - timezone.timedelta(days=7)
        last_30_days = now - timezone.timedelta(days=30)
        last_1_year = now - timezone.timedelta(days=365)

        # Range-scoped stats
        orders_range = paid_orders.filter(
            created_at__gte=start,
            created_at__lte=end
        ).count()
        revenue_range = (
            OrderItem.objects.filter(
                order__status="paid",
                order__created_at__gte=start,
                order__created_at__lte=end,
            ).aggregate(total=Coalesce(Sum(line_amount_expr), Decimal("0")))
        )["total"] or Decimal("0")
        new_users_range = User.objects.filter(
            date_joined__gte=start,
            date_joined__lte=end
        ).count()
        new_reviews_range = ProductReview.objects.filter(
            created_at__gte=start,
            created_at__lte=end
        ).count()

        # 7-day stats
        orders_7d = paid_orders.filter(created_at__gte=last_7_days).count()
        revenue_7d = (
            OrderItem.objects.filter(
                order__status="paid",
                order__created_at__gte=last_7_days
            ).aggregate(
                total=Coalesce(Sum(line_amount_expr), Decimal("0"))
            )
        )["total"] or Decimal("0")
        new_users_7d = User.objects.filter(date_joined__gte=last_7_days).count()
        new_reviews_7d = (
            ProductReview.objects.filter(created_at__gte=last_7_days)
            .count()
        )

        # 30-day stats
        orders_30d = paid_orders.filter(created_at__gte=last_30_days).count()
        revenue_30d = (
            OrderItem.objects.filter(
                order__status="paid",
                order__created_at__gte=last_30_days
            ).aggregate(total=Coalesce(Sum(line_amount_expr), Decimal("0")))
        )["total"] or Decimal("0")
        new_users_30d = User.objects.filter(
            date_joined__gte=last_30_days
        ).count()
        new_reviews_30d = (
            ProductReview.objects.filter(created_at__gte=last_30_days)
            .count()
        )

        # 1-year stats
        orders_1y = paid_orders.filter(created_at__gte=last_1_year).count()
        revenue_1y = (
            OrderItem.objects.filter(
                order__status="paid",
                order__created_at__gte=last_1_year
            ).aggregate(total=Coalesce(Sum(line_amount_expr), Decimal("0")))
        )["total"] or Decimal("0")
        new_users_1y = User.objects.filter(date_joined__gte=last_1_year).count()
        new_reviews_1y = (
            ProductReview.objects.filter(created_at__gte=last_1_year)
            .count()
        )

        ctx.update(
            {
                "kpi": {
                    "users": {
                        "total": total_users,
                        "active": active_users,
                        "suspended": suspended_users,
                        "staff": staff_users,
                        "superusers": superusers,
                        "new_range": new_users_range,
                        "new_7d": new_users_7d,
                        "new_30d": new_users_30d,
                        "new_1y": new_users_1y,
                    },
                    "catalog": {
                        "shops": total_shops,
                        "products": total_products,
                        "active_products": active_products,
                        "inactive_products": inactive_products,
                        "reviews_range": new_reviews_range,
                        "reviews_7d": new_reviews_7d,
                        "reviews_30d": new_reviews_30d,
                        "reviews_1y": new_reviews_1y,
                    },
                    "sales": {
                        "orders": total_orders,
                        "gross_revenue": gross_revenue,
                        "orders_range": orders_range,
                        "revenue_range": revenue_range,
                        "orders_7d": orders_7d,
                        "revenue_7d": revenue_7d,
                        "orders_30d": orders_30d,
                        "revenue_30d": revenue_30d,
                        "orders_1y": orders_1y,
                        "revenue_1y": revenue_1y,
                    },
                },
            }
        )
        return ctx
