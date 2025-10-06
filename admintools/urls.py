from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.DashboardView.as_view(), name="index"),
    path("users/", views.UserListView.as_view(), name="users"),
    path("shops/", views.ShopsProductsView.as_view(), name="shops_products"),
    path("reports/", views.ReportsView.as_view(), name="reports"),
    path("reviews/", views.ReviewsListView.as_view(), name="reviews"),
    path(
        "reviews/<int:pk>/toggle/",
        views.review_toggle_visibility,
        name="review_toggle_visibility"
    ),
    path(
        "reports/export.csv",
        views.reports_export_csv,
        name="reports_export_csv"
    ),
    path(
        "reports/export-products.csv",
        views.reports_export_products_csv,
        name="reports_export_products_csv"
    ),
    path(
        "users/<int:pk>/toggle-staff/",
        views.user_toggle_staff,
        name="user_toggle_staff"
    ),
    path(
        "users/<int:pk>/toggle-suspend/",
        views.user_toggle_suspend,
        name="user_toggle_suspend"
    ),
    path(
        "products/<int:pk>/suspend/",
        views.product_toggle_suspend,
        name="product_toggle_suspend"
    ),
]
