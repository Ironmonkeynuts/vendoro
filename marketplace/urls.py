from django.urls import path
from . import views

app_name = "marketplace"

urlpatterns = [
    path(
        "seller/",
        views.seller_dashboard,
        name="seller"
    ),
    path(
        "seller/reviews/<int:review_id>/reply/",
        views.review_reply,
        name="review_reply"
    ),
    path("", views.ProductList.as_view(), name="browse"),
    path("cloudinary/sign/", views.cloudinary_sign, name="cloudinary_sign"),
    # Shop creation
    path("shops/new/", views.shop_create, name="shop_create"),
    # Shop settings
    path(
        "shops/<slug:slug>/settings/",
        views.shop_settings,
        name="shop_settings"
    ),
        path(
        "shops/<slug:slug>/banner/update/",
        views.update_shop_banner,
        name="shop_banner_update"
    ),
    path("shops/<slug:slug>/products/new/",
         views.product_create,
         name="product_create"
    ),
    # Shop details
    path(
        "shops/<slug:slug>/",
        views.shop_detail,
        name="shop_detail"
    ),
    # Product management
    path(
        "products/<int:pk>/edit/",
        views.product_edit,
        name="product_edit"
    ),
    path(
        "product/<int:pk>/images/attach/",
        views.attach_product_image,
        name="product_image_attach"
    ),
    path(
        "products/<int:pk>/images/<int:image_id>/remove/",
        views.product_image_remove,
        name="product_image_remove"
    ),
    # Generic product detail
    path(
        "shops/<slug:shop_slug>/<slug:product_slug>/",
        views.product_detail,
        name="product_detail"
    ),
    path(
        "shops/<slug:shop_slug>/<slug:product_slug>/review/",
        views.review_add,
        name="review_add",
    ),
]
