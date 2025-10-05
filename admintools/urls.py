from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.DashboardView.as_view(), name="index"),
    path("users/", views.UserListView.as_view(), name="users"),
    path("users/<int:pk>/toggle-staff/", views.user_toggle_staff, name="user_toggle_staff"),
    path("users/<int:pk>/toggle-suspend/", views.user_toggle_suspend, name="user_toggle_suspend"),
]
