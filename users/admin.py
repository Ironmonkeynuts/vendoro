from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as Base
from .models import User, BuyerProfile, SellerProfile


@admin.register(User)
class UserAdmin(Base):
    fieldsets = Base.fieldsets + (("Role", {"fields": ("user_type",)}),)
    list_display = (
        "username",
        "email",
        "user_type",
        "is_staff",
        "is_superuser",
    )


admin.site.register(BuyerProfile)
admin.site.register(SellerProfile)
