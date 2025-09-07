import json
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import (
    HttpResponseBadRequest,
    HttpResponseForbidden,
    JsonResponse
)
from django.db.models import Q
from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.http import require_GET, require_POST
from django.views.generic import ListView
from cloudinary.utils import api_sign_request
from .models import Shop, Product, ProductImage
from .forms import ProductForm, ShopForm


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
            .order_by("-created_at")
        )
        q = self.request.GET.get("q")
        cat = self.request.GET.get("category")
        sort = self.request.GET.get("sort")
        if q:
            qs = qs.filter(
                Q(title__icontains=q) | Q(description__icontains=q) |
                Q(shop__name__icontains=q) | Q(category__name__icontains=q)
            )
        if cat:
            qs = qs.filter(category__slug=cat)
        # qs = qs.annotate(avg_rating=Avg("reviews__rating"))
        if sort == "price_asc":
            qs = qs.order_by("price")
        elif sort == "price_desc":
            qs = qs.order_by("-price")
        return qs


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
    context = {
        "product": product,
        "product_images": product_images,
    }
    return render(
        request, "marketplace/product_detail.html", context
    )


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
    return product.shop.owner_id == user.id


def _owns_shop(user, shop):
    return shop.owner_id == user.id


@login_required
def product_edit(request, pk):
    """
    Edit a product.
    """
    if not request.user.is_authenticated:
        return redirect("account:login")
    product = get_object_or_404(Product, pk=pk)
    if not _owns_product(request.user, product):
        return HttpResponseForbidden("Not your product")

    if request.method == "POST":
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, "Product updated.")
            return redirect("marketplace:product_edit", pk=product.pk)
    else:
        form = ProductForm(instance=product)

    return render(
        request,
        "marketplace/product_edit.html",
        {"product": product, "form": form},
    )


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
@require_GET
def cloudinary_sign(request):
    """
    Sign a Cloudinary upload request.
    """
    params = request.GET.dict()
    folder = params.get("folder")
    if folder not in ALLOWED_FOLDERS.values():
        return HttpResponseBadRequest("Invalid folder")
    signature = api_sign_request(
        params, settings.CLOUDINARY_STORAGE["API_SECRET"]
    )
    return JsonResponse({"signature": signature})


@login_required
@require_POST
def attach_product_image(request, pk):
    """
    Attach an image to a product.
    """
    product = get_object_or_404(Product, pk=pk)
    if not _owns_product(request.user, product):
        return HttpResponseForbidden("Not your product")
    try:
        data = json.loads(request.body.decode("utf-8"))
        public_id = data["public_id"]
        alt_text = data.get("alt_text", "")
    except Exception:
        return HttpResponseBadRequest("Invalid payload")
    ProductImage.objects.create(
        product=product, image=public_id, alt_text=alt_text
    )
    return JsonResponse({"ok": True})


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
    Create a product under a shop (owner only).
    After save, jump to Edit (to add images).
    """
    shop = get_object_or_404(Shop, slug=slug)
    if not _owns_shop(request.user, shop):
        return HttpResponseForbidden("Not your shop")

    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            product.shop = shop
            product.save()
            messages.success(request, "Product created. Add images below.")
            return redirect("marketplace:product_edit", pk=product.pk)
    else:
        form = ProductForm()

    return render(
        request,
        "marketplace/product_create.html",
        {"shop": shop, "form": form}
    )
