from django.urls import path
from . import views

app_name = "orders"

urlpatterns = [
    path("cart/", views.cart_detail, name="cart_detail"),
    path("cart/add/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path(
        "cart/item/<int:item_id>/update/",
        views.update_quantity,
        name="update_quantity"
    ),
    path(
        "cart/item/<int:item_id>/delete/",
        views.remove_item,
        name="remove_item"
    ),
    path("cart/clear/", views.clear_cart, name="clear_cart"),
    path("myorders/", views.my_orders, name="my_orders"),
    path(
        "email-preview/<int:order_id>/",
        views.email_debug_preview,
        name="email_debug_preview",
    ),
]
