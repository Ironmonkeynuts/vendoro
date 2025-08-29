from django.contrib import admin
from .models import (
    Shop,
    Category,
    Product,
    ProductImage,
    Inventory
)


admin.site.register(Shop)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(ProductImage)
admin.site.register(Inventory)
