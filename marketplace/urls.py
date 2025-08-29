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
]
