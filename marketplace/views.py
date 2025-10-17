import json
import csv
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.db.models import (
    Avg, Count, Q, F, Sum, DecimalField, ExpressionWrapper
)
from django.db.models.functions import Coalesce, TruncDate
from django.http import (
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseForbidden,
    JsonResponse
)
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.views.decorators.http import (
    require_POST, require_http_methods
)
from django.views.generic import ListView
from cloudinary.utils import api_sign_request, cloudinary_url
from cloudinary.uploader import destroy as cl_destroy
from decimal import Decimal
from datetime import datetime, time
from .models import (
    Shop,
    Product,
    ProductImage,
    ProductReview,
    Category
)
from orders.models import Order, OrderItem
from users.models import SellerProfile
from .forms import ProductForm, ShopForm, ProductReviewForm, SellerProfileForm


# --- shared range parser (seller-side) ---
def _parse_range(request, default_days: int = 7):
    """
    Parse ?range=7|30|90|custom&start=YYYY-MM-DD&end=YYYY-MM-DD
    Return (start_dt_aware, end_dt_aware).
    """
    now = timezone.now()
    rng = (request.GET.get("range") or str(default_days)).strip()
    start_param = request.GET.get("start")
    end_param = request.GET.get("end")

    if rng in {"7", "30", "90"}:
        start = now - timezone.timedelta(days=int(rng))
        end = now
        label = rng
    else:
        sd = parse_date(start_param) if start_param else None
        ed = parse_date(end_param) if end_param else None
        start = (
            timezone.make_aware(datetime.combine(sd, time.min))
            if sd else now - timezone.timedelta(days=default_days)
        )
        end = (
            timezone.make_aware(datetime.combine(ed, time.max))
            if ed else now
        )
        label = "custom"

    return start, end, label


@login_required
def seller_export_timeseries(request):
    """
    CSV: per-day orders/items/revenue for THIS seller across their shops
    respecting the selected range.
    """
    start, end, _ = _parse_range(request)

    # only the seller's items (paid orders)
    line_amount = ExpressionWrapper(
        F("quantity") * F("unit_price"),
        output_field=DecimalField(max_digits=12, decimal_places=2),
    )

    daily = (
        OrderItem.objects.filter(
            product__shop__owner=request.user,
            order__status="paid",
            order__created_at__gte=start,
            order__created_at__lte=end,
        )
        .annotate(day=TruncDate("order__created_at"))
        .values("day")
        .annotate(
            orders=Count("order_id", distinct=True),
            items=Coalesce(Sum("quantity"), 0),
            revenue=Coalesce(Sum(line_amount), Decimal("0")),
        )
        .order_by("day")
    )

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = (
        f'attachment; filename="seller_timeseries_{start.date()}_'
        f'{end.date()}.csv"'
    )
    writer = csv.writer(response)
    writer.writerow(["date", "orders", "items", "revenue"])
    for row in daily:
        writer.writerow([
            row["day"].isoformat(),
            row["orders"],
            int(row["items"] or 0),
            f'{row["revenue"]:.2f}'
        ])
    return response


@login_required
def seller_export_products(request):
    """
    CSV: orders/items/revenue by product for THIS seller
    for the selected range.
    """
    start, end, _ = _parse_range(request)

    line_amount = ExpressionWrapper(
        F("quantity") * F("unit_price"),
        output_field=DecimalField(max_digits=12, decimal_places=2),
    )

    qs = (
        OrderItem.objects.filter(
            product__shop__owner=request.user,
            order__status="paid",
            order__created_at__gte=start,
            order__created_at__lte=end,
        )
        .values(
            "product_id",
            "product__title",
            "product__slug",
            "product__shop__name",
            "product__shop__slug",
        )
        .annotate(
            orders=Count("order_id", distinct=True),
            items_sold=Coalesce(Sum("quantity"), 0),
            revenue=Coalesce(Sum(line_amount), Decimal("0")),
        )
        .order_by("-revenue", "-items_sold", "-orders")
    )

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = (
        (
            f'attachment; filename="seller_products_{start.date()}_'
            f'{end.date()}.csv"'
        )
    )
    writer = csv.writer(response)
    writer.writerow([
        "product_id", "product_title", "shop_name",
        "orders", "items_sold", "revenue"
    ])
    for row in qs:
        writer.writerow([
            row["product_id"],
            row["product__title"],
            row["product__shop__name"],
            row["orders"],
            int(row["items_sold"] or 0),
            f'{row["revenue"]:.2f}',
        ])
    return response


class ProductList(ListView):
    """
    Display a list of products with search and sort functionality.
    """
    allow_empty = True
    template_name = "marketplace/product_list.html"
    model = Product
    paginate_by = 12

    def get_queryset(self):
        qs = (
            Product.objects.filter(is_active=True)
            .select_related("shop", "category")
            .prefetch_related("images")
        )

        q = (self.request.GET.get("q") or "").strip()
        cat_slug = (
            self.request.GET.get("category") or
            self.request.GET.get("cat") or ""
        ).strip()
        sort = (self.request.GET.get("sort") or "").strip()

        if q:
            qs = qs.filter(
                Q(title__icontains=q)
                | Q(description__icontains=q)
                | Q(shop__name__icontains=q)
            )

        if cat_slug:
            qs = qs.filter(category__slug=cat_slug)

        if sort == "price_asc":
            qs = qs.order_by("price", "-id")
        elif sort == "price_desc":
            qs = qs.order_by("-price", "-id")
        else:
            qs = qs.order_by("-created_at")

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["categories"] = Category.objects.order_by("name")
        ctx["q"] = (self.request.GET.get("q") or "").strip()
        ctx["active_category"] = (
            self.request.GET.get("category") or
            self.request.GET.get("cat") or ""
        ).strip()
        ctx["sort"] = (self.request.GET.get("sort") or "").strip()
        return ctx


def product_detail(request, shop_slug, product_slug):
    """
    Display the details of a specific product.
    """
    product = get_object_or_404(
        Product.objects.select_related("shop", "category"),
        shop__slug=shop_slug,
        slug=product_slug,
        is_active=True
    )
    product_images = ProductImage.objects.filter(product=product)

    # Get reviews and aggregate stats
    reviews = (
        product.reviews
        .select_related("user", "reply", "product__shop")  # reply is OneToOne
        .order_by("-created_at")
    )
    rating_stats = reviews.aggregate(
        avg=Avg("rating"),
        count=Count("id"),
    )
    already_reviewed = (
        request.user.is_authenticated and
        reviews.filter(user=request.user).exists()
    )
    # Context for template
    context = {
        "product": product,
        "product_images": product_images,
        "reviews": reviews,
        "rating_avg": rating_stats["avg"] or 0,
        "rating_count": rating_stats["count"] or 0,
        "already_reviewed": already_reviewed,
    }
    return render(
        request, "marketplace/product_detail.html", context
    )


@login_required
def seller_profile(request):
    # Ensure SellerProfile exists
    sp, _ = SellerProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = SellerProfileForm(request.POST, instance=sp)
        if form.is_valid():
            form.save()
            messages.success(request, "Seller profile updated.")
            return redirect("marketplace:seller_profile")
        messages.error(request, "Please correct the errors below.")
    else:
        form = SellerProfileForm(instance=sp)

    return render(request, "marketplace/seller_profile.html", {"form": form})


@login_required
def shop_create(request):
    """
    Create a new shop (owner = request.user),
    then jump to settings to add banner etc.
    """
    if request.method == "POST":
        form = ShopForm(request.POST, owner=request.user)
        if form.is_valid():
            shop = form.save(commit=False)
            shop.owner = request.user
            try:
                shop.save()
            except IntegrityError:
                form.add_error(
                    "name",
                    "You already have a shop with this name."
                )
            else:
                messages.success(
                    request,
                    "Shop created! Configure your shop settings below."
                )
                return redirect("marketplace:shop_settings", slug=shop.slug)
    else:
        form = ShopForm(owner=request.user)

    return render(request, "marketplace/shop_create.html", {"form": form})


def _shop_banner_url(shop, *, width=1600, height=420):
    """
    Return a transformed Cloudinary URL for the shop banner if possible.
    Works with CloudinaryField (public_id) and django-cloudinary-storage (name).
    Falls back to the storage URL if transformation isn't possible.
    """
    if not getattr(shop, "banner", None):
        return None

    # Try to get something we can hand to cloudinary_url
    public_id = (
        getattr(shop.banner, "public_id", None)  # CloudinaryField
        or getattr(shop.banner, "name", None)    # django-cloudinary-storage path
        or str(shop.banner)                       # last resort
    )

    try:
        url, _ = cloudinary_url(
            public_id,
            width=width,
            height=height,
            crop="fill",
            gravity="auto",
            fetch_format="auto",
            quality="auto",
        )
        return url
    except Exception:
        # Fallback to the raw file URL (no transforms)
        try:
            return shop.banner.url
        except Exception:
            return None


def shop_detail(request, slug):
    """
    Display the details of a specific shop.
    """
    shop = get_object_or_404(Shop, slug=slug)
    products = shop.products.filter(is_active=True).order_by("-created_at")

    banner_url = _shop_banner_url(shop)

    return render(
        request,
        "marketplace/shop_detail.html",
        {
            "shop": shop,
            "products": products,
            "banner_url": banner_url,
        },
    )


ALLOWED_FOLDERS = {
    "product": "vendoro/product_images",
    "banner": "vendoro/shop_banners",
}


def _owns_product(user, product):
    return user.is_authenticated and product.shop.owner_id == user.id


def _owns_shop(user, shop):
    return user.is_authenticated and shop.owner_id == user.id


@login_required
def shop_settings(request, slug):
    """
    Edit shop settings.
    """
    if not request.user.is_authenticated:
        return redirect("account:login")
    shop = get_object_or_404(Shop, slug=slug)
    if not _owns_shop(request.user, shop):
        return HttpResponseForbidden("Not your shop")

    if request.method == "POST":
        form = ShopForm(request.POST, instance=shop)
        if form.is_valid():
            form.save()
            messages.success(request, "Shop settings saved.")
            return redirect("marketplace:shop_settings", slug=shop.slug)
    else:
        form = ShopForm(instance=shop)

    return render(
        request,
        "marketplace/shop_settings.html",
        {"shop": shop, "form": form},
    )


@login_required
@require_http_methods(["GET", "POST"])
def cloudinary_sign(request):
    """
    Sign parameters for Cloudinary Upload Widget.
    Accepts params via querystring.
    """
    params = request.GET.dict()
    folder = params.get("folder")
    if folder not in ALLOWED_FOLDERS.values():
        return HttpResponseBadRequest("Invalid folder")

    secret = settings.CLOUDINARY_STORAGE.get("API_SECRET")
    if not secret:
        return HttpResponseBadRequest("Missing API secret")
    signature = api_sign_request(params, secret)
    return JsonResponse({"signature": signature})


ALLOWED_PUBLIC_ID_PREFIX = "vendoro/product_images/"


@login_required
@require_POST
def attach_product_image(request, pk):
    """
    Attach a Cloudinary image (by public_id) to a product.
    Expects JSON: {"public_id": "...", "alt_text": "..."}
    """
    product = get_object_or_404(Product, pk=pk)
    if not _owns_product(request.user, product):
        return HttpResponseForbidden("Not your product")

    try:
        data = json.loads(request.body.decode("utf-8"))
        # validate public_id
        public_id = data["public_id"].strip()
        alt_text = data.get("alt_text", "").strip()
        if not public_id:
            raise ValueError("missing public_id")
    except Exception:
        return HttpResponseBadRequest("Invalid payload")

    pi = ProductImage.objects.create(
        product=product,
        # CloudinaryField accepts the public_id string
        image=public_id,
        alt_text=alt_text,
    )
    return JsonResponse(
        {
            "ok": True,
            "id": pi.id,
            "public_id": public_id,
            "alt_text": alt_text
        },
        status=201,
    )


@login_required
@require_POST
def product_image_remove(request, pk, image_id):
    """
    Remove an image from a product (delete DB row).
    If 'purge=1' is posted, also delete the Cloudinary asset.
    Owner-only.
    """
    product = get_object_or_404(Product, pk=pk)
    if not _owns_product(request.user, product):
        return HttpResponseForbidden("Not your product")

    pi = get_object_or_404(ProductImage, pk=image_id, product=product)

    # Purge of the actual Cloudinary asset
    if request.POST.get("purge") == "1":
        public_id = getattr(pi.image, "public_id", None) or str(pi.image)
        if not str(public_id).startswith(ALLOWED_PUBLIC_ID_PREFIX):
            return HttpResponseBadRequest(
                "Refusing to purge disallowed public_id"
            )
        try:
            cl_destroy(public_id, invalidate=True)
        except Exception:
            pass  # ignore Cloudinary errors

    pi.delete()

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({"ok": True})

    messages.success(request, "Image removed.")
    return redirect("marketplace:product_edit", pk=product.pk)


@login_required
@require_POST
def update_shop_banner(request, slug):
    """
    Update the shop banner.
    """
    shop = get_object_or_404(Shop, slug=slug)
    if not _owns_shop(request.user, shop):
        return HttpResponseForbidden("Not your shop")
    try:
        data = json.loads(request.body.decode("utf-8"))
        public_id = data["public_id"]
    except Exception:
        return HttpResponseBadRequest("Invalid payload")
    shop.banner = public_id
    shop.save(update_fields=["banner"])
    return JsonResponse({"ok": True})


@login_required
def product_create(request, slug):
    """
    Create a product under a shop (owner only), then PRG redirect to edit.
    """
    shop = get_object_or_404(Shop, slug=slug)
    if not _owns_shop(request.user, shop):
        return HttpResponseForbidden("Not your shop")

    if request.method == "POST":
        form = ProductForm(request.POST, shop=shop)
        if form.is_valid():
            product = form.save(commit=False)
            product.shop = shop
            try:
                product.save()
            except IntegrityError:
                form.add_error(
                    "title",
                    "A product with this title already exists in this shop."
                )
            else:
                messages.success(request, "Product created. Add images below.")
                return redirect("marketplace:product_edit", pk=product.pk)
    else:
        form = ProductForm(shop=shop)

    return render(
        request, "marketplace/product_create.html",
        {"shop": shop, "form": form}
    )


@login_required
def product_edit(request, pk):
    """
    Edit a product.
    """
    product = get_object_or_404(Product, pk=pk)
    if not _owns_product(request.user, product):
        return HttpResponseForbidden("Not your product")

    if request.method == "POST":
        form = ProductForm(
            request.POST,
            instance=product,
            shop=product.shop
        )
        if form.is_valid():
            try:
                form.save()
            except IntegrityError:
                form.add_error(
                    "title",
                    "A product with this title already exists in this shop."
                )
            else:
                messages.success(request, "Product updated.")
                return redirect("marketplace:product_edit", pk=product.pk)
    else:
        form = ProductForm(instance=product, shop=product.shop)

    return render(
        request,
        "marketplace/product_edit.html",
        {"product": product, "form": form},
    )


@login_required
def review_add(request, shop_slug, product_slug):
    product = get_object_or_404(
        Product.objects.select_related("shop"),
        shop__slug=shop_slug,
        slug=product_slug,
        is_active=True,
    )

    # one review per user/product
    if ProductReview.objects.filter(
        product=product, user=request.user
    ).exists():
        messages.info(request, "You have already reviewed this product.")
        return redirect(
            "marketplace:product_detail",
            shop_slug=shop_slug,
            product_slug=product_slug,
        )
    # must have at least one completed order for this product
    has_completed = OrderItem.objects.filter(
        order__user=request.user,
        product=product,
        order__fulfillment_status="completed",
    ).exists()
    if not has_completed:
        messages.error(
            request,
            "You can only review products you’ve purchased."
        )
        return redirect(
            "marketplace:product_detail",
            shop_slug=shop_slug,
            product_slug=product_slug,
        )
    if request.method == "POST":
        form = ProductReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            messages.success(request, "Thanks for your review!")
            return redirect(
                "marketplace:product_detail",
                shop_slug=shop_slug,
                product_slug=product_slug
            )
    else:
        form = ProductReviewForm()

    return render(
        request,
        "marketplace/review_form.html",
        {"form": form, "product": product}
    )


@login_required
def seller_dashboard(request):
    """
    Seller dashboard with tabs:
    - Inventory (unchanged)
    - Alerts (recent transactions & reviews; unchanged)
    - Stats (now range-aware + CSV export support)
    """
    has_shop = Shop.objects.filter(owner=request.user).exists()
    if not has_shop:
        return redirect("marketplace:shop_create")
    
    start, end, label = _parse_range(request)

    # INVENTORY
    products = (
        Product.objects
        .filter(shop__owner=request.user, is_active=True)
        .select_related("shop", "category")
        .annotate(
            review_count=Count("reviews", distinct=True),
            review_avg=Avg("reviews__rating"),
        )
        .order_by("shop__name", "-created_at")
    )
    by_shop = {}
    for p in products:
        by_shop.setdefault(p.shop, []).append(p)

    # ORDERS (each order belongs to one shop)
    orders_qs = (
        Order.objects
        .filter(shop__owner=request.user)
        .select_related("user", "shop")
        .order_by("-created_at")
    )

    orders_by_shop = {}
    for order in orders_qs:
        orders_by_shop.setdefault(order.shop, []).append(order)

    # choices for the fulfillment dropdown
    try:
        fulfillment_choices = Order._meta.get_field("fulfillment_status").choices
    except Exception:
        fulfillment_choices = getattr(getattr(Order, "FulfillmentStatus", None), "choices", [])

    # ALERTS
    recent_items = (
        OrderItem.objects
        .filter(product__shop__owner=request.user)
        .select_related("order", "product", "product__shop", "order__user")
        .order_by("-order__created_at")[:20]
    )
    new_reviews = (
        ProductReview.objects
        .filter(product__shop__owner=request.user)
        .select_related("product", "product__shop", "user")
        .order_by("-created_at")[:20]
    )

    # STATS (range-aware)
    sale_statuses = ["paid", "completed"]
    items_qs = (
        OrderItem.objects
        .filter(
            product__shop__owner=request.user,
            order__status__in=sale_statuses,
            order__created_at__gte=start,
            order__created_at__lte=end,
        )
        .select_related("product", "product__shop")
    )

    # KPI calculations
    revenue_expr = ExpressionWrapper(
        F("unit_price") * F("quantity"),
        output_field=DecimalField(max_digits=12, decimal_places=2),
    )

    agg = items_qs.aggregate(
        orders=Count("order_id", distinct=True),
        items=Coalesce(Sum("quantity"), 0),
        revenue=Coalesce(Sum(revenue_expr), Decimal("0")),
    )

    reviews_in_range = ProductReview.objects.filter(
        product__shop__owner=request.user,
        created_at__gte=start,
        created_at__lte=end,
    ).count()

    active_products = Product.objects.filter(
        shop__owner=request.user, is_active=True
    ).count()

    aov = (agg["revenue"] / agg["orders"]) if agg["orders"] else Decimal("0")

    kpi = {
        "orders": agg["orders"] or 0,
        "items": int(agg["items"] or 0),
        "revenue": agg["revenue"] or Decimal("0"),
        "reviews": reviews_in_range,
        "active_products": active_products,
        "aov": aov,
    }

    per_product = (
        items_qs
        .values(
            "product_id", "product__title", "product__slug",
            "product__shop_id", "product__shop__name", "product__shop__slug"
        )
        .annotate(
            qty_sold=Coalesce(Sum("quantity"), 0),
            revenue=Coalesce(Sum(revenue_expr), Decimal("0")),
        )
        .order_by("-revenue", "-qty_sold")
    )

    top_5 = list(per_product[:5])
    lowest_5 = list(per_product.order_by("revenue", "qty_sold")[:5])

    stats_by_shop = {}
    for row in per_product:
        key = (
            row["product__shop_id"],
            row["product__shop__name"],
            row["product__shop__slug"],
        )
        stats_by_shop.setdefault(key, []).append(row)

    active_tab = (request.GET.get("tab") or "inventory").strip()

    context = {
        "inventory_by_shop": by_shop,
        "orders_by_shop": orders_by_shop,
        "fulfillment_choices": fulfillment_choices,
        "recent_items": recent_items,
        "new_reviews": new_reviews,
        "stats_by_shop": stats_by_shop,
        "top_5": top_5,
        "lowest_5": lowest_5,
        # pass range + kpis to the Stats tab
        "range": {"label": label, "start": start.date(), "end": end.date()},
        "kpi": kpi,
        "active_tab": active_tab,
    }

    return render(request, "marketplace/seller_dashboard.html", context)


@login_required
@require_POST
def seller_update_fulfillment(request, order_id):
    """
    Seller can update fulfillment_status on their own shop's order.
    Single-shop orders only (current behavior).
    """
    order = get_object_or_404(Order.objects.select_related("shop", "user"), id=order_id)

    # Authorize: must be this seller's shop
    if order.shop.owner_id != request.user.id:
        messages.error(request, "You cannot update fulfillment for this order.")
        return redirect(f"{reverse('marketplace:seller')}?tab=orders")

    # Validate and update
    field = Order._meta.get_field("fulfillment_status")
    valid = {k for k, _ in field.choices}
    new_value = (request.POST.get("fulfillment_status") or "").strip()

    if new_value not in valid:
        messages.error(request, "Invalid fulfillment status.")
    else:
        order.fulfillment_status = new_value
        order.save(update_fields=["fulfillment_status"])
        messages.success(
            request,
            f"Order #{order.id} updated to {order.get_fulfillment_status_display()}."
        )

    # Keep Orders tab active
    return redirect(f"{reverse('marketplace:seller')}?tab=orders")


@login_required
def review_reply(request, review_id):
    review = get_object_or_404(
        ProductReview,
        pk=review_id,
        product__shop__owner=request.user,  # ownership check
    )
    if request.method == "POST":
        body = (request.POST.get("body") or "").strip()
        if not body:
            messages.error(request, "Reply cannot be empty.")
        else:
            # TODO: persist the reply (model/field as you prefer)
            messages.success(request, "Reply saved (stub).")
    return redirect("marketplace:seller")
