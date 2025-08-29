from django.urls import path
from . import views

app_name = "orders"

urlpatterns = [
    path("cart/", views.cart_detail, name="cart_detail"),
    path("cart/add/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("cart/item/<int:item_id>/qty/", views.update_quantity, name="update_quantity"),
    path("cart/item/<int:item_id>/remove/", views.remove_item, name="remove_item"),
]
