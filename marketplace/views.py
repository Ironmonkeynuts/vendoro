import json
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.db.models import Avg, Count
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
        qs = (Product.objects.filter(is_active=True)
              .select_related("shop")
              .prefetch_related("images"))
        q = self.request.GET.get("q")
        if q:
            qs = qs.filter(title__icontains=q)
        sort = self.request.GET.get("sort")
        if sort == "price_asc":
            qs = qs.order_by("price", "-id")
        elif sort == "price_desc":
            qs = qs.order_by("-price", "-id")
        else:
            qs = qs.order_by("-created_at")
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
    rating_stats = product.reviews.aggregate(
        avg=Avg("rating"),
        count=Count("id"),
    )
    context = {
        "product": product,
        "product_images": product_images,
        "rating_avg": rating_stats["avg"],
        "rating_count": rating_stats["count"],
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
