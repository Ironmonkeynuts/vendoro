import json
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.db.models import (
    Avg, Count, Q, F, Sum, DecimalField, ExpressionWrapper
)
from django.http import (
    HttpResponseBadRequest,
    HttpResponseForbidden,
    JsonResponse
)
from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.http import (
    require_POST, require_http_methods
)
from django.views.generic import ListView
from cloudinary.utils import api_sign_request
from cloudinary.uploader import destroy as cl_destroy
from .models import (
    Shop,
    Product,
    ProductImage,
    ProductReview,
    Category
)
from orders.models import OrderItem
from .forms import ProductForm, ShopForm, ProductReviewForm


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
        .select_related("user")           # avoid N+1 on user
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


def shop_detail(request, slug):
    """
    Display the details of a specific shop.
    """
    shop = get_object_or_404(Shop, slug=slug)
    # shop.products is the reverse ForeignKey from Product model
    products = shop.products.filter(is_active=True).order_by("-created_at")
    return render(
        request, "marketplace/shop_detail.html",
        {"shop": shop, "products": products}
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
    Display a dashboard for the seller with their shops and products.
    Shell with tabs. Requires the user to own a shop.
    """
    has_shop = Shop.objects.filter(owner=request.user).exists()
    if not has_shop:
        # nudge them to create a shop first
        return redirect("marketplace:shop_create")

    # Prefetch products and annotate review stats
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

    # group by shop id in memory for simple rendering
    by_shop = {}
    for p in products:
        by_shop.setdefault(p.shop, []).append(p)

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

    sale_statuses = ["paid", "completed"]  # adjust if your enum differs
    items_qs = (
        OrderItem.objects
        .filter(
            product__shop__owner=request.user,
            order__status__in=sale_statuses
        )
        .select_related("product", "product__shop")
    )

    revenue_expr = ExpressionWrapper(
        F("unit_price") * F("quantity"),
        output_field=DecimalField(max_digits=12, decimal_places=2),
    )

    per_product = (
        items_qs
        .values(
            "product_id", "product__title", "product__slug",
            "product__shop_id", "product__shop__name",
            "product__shop__slug"
        )
        .annotate(
            qty_sold=Sum("quantity"),
            revenue=Sum(revenue_expr),
        )
        .order_by("-qty_sold", "-revenue")
    )

    # Top and bottom slices
    top_5 = list(per_product[:5])
    lowest_5 = list(per_product.order_by("qty_sold", "revenue")[:5])

    # Group by shop for the main stats table
    stats_by_shop = {}
    for row in per_product:
        key = (
            row["product__shop_id"],
            row["product__shop__name"],
            row["product__shop__slug"],
        )
        stats_by_shop.setdefault(key, []).append(row)

    context = {
        "inventory_by_shop": by_shop,
        "recent_items": recent_items,
        "new_reviews": new_reviews,
        "stats_by_shop": stats_by_shop,
        "top_5": top_5,
        "lowest_5": lowest_5,
    }
    return render(request, "marketplace/seller_dashboard.html", context)


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
