from django.db.models import Q
from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView
from .models import Product, Shop, ProductImage


class ProductList(ListView):
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
            qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q) | Q(shop__name__icontains=q) | Q(category__name__icontains=q))
        if cat:
            qs = qs.filter(category__slug=cat)
        # qs = qs.annotate(avg_rating=Avg("reviews__rating"))
        if sort == "price_asc":
            qs = qs.order_by("price")
        elif sort == "price_desc":
            qs = qs.order_by("-price")
        return qs


def product_detail(request, shop_slug, product_slug):
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
    shop = get_object_or_404(Shop, slug=slug)
    # shop.products is the reverse ForeignKey from Product model
    products = shop.products.filter(is_active=True).order_by("-created_at")
    return render(
        request, "marketplace/shop_detail.html",
        {"shop": shop, "products": products})
