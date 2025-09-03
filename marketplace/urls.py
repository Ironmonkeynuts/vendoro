from django.urls import path
from . import views

app_name = "marketplace"

urlpatterns = [
    path("", views.ProductList.as_view(), name="browse"),
    path("shops/<slug:slug>/", views.shop_detail, name="shop_detail"),
    path(
        "shops/<slug:shop_slug>/<slug:product_slug>/",
        views.product_detail,
        name="product_detail"
    ),
    path("cloudinary/sign/", views.cloudinary_sign, name="cloudinary_sign"),
    path(
        "product/<int:pk>/images/attach/",
        views.attach_product_image,
        name="product_image_attach"
    ),
    path(
        "shops/<slug:slug>/banner/update/",
        views.update_shop_banner,
        name="shop_banner_update"
    ),
]
