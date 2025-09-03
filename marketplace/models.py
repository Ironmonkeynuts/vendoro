from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.text import slugify
from cloudinary.models import CloudinaryField


User = settings.AUTH_USER_MODEL


class Shop(models.Model):
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='shops'
    )
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    tagline = models.CharField(max_length=255, blank=True)
    primary_color = models.CharField(max_length=7, default='#111827')
    highlight_color = models.CharField(max_length=7, default='#06b6d4')
    banner = CloudinaryField(
        'image',
        folder='vendoro/shop_banners',
        blank=True,
        null=True
    )

    class Meta:
        unique_together = ('owner', 'name')

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name)
            candidate = base
            i = 1
            from django.db.models import Q
            while Shop.objects.filter(Q(slug=candidate)).exists():
                i += 1
                candidate = f"{base}-{i}"
            self.slug = candidate
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(unique=True, blank=True)

    class Meta:
        verbose_name_plural = 'categories'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(models.Model):
    shop = models.ForeignKey(
        Shop, on_delete=models.CASCADE, related_name='products'
    )
    title = models.CharField(max_length=255)
    slug = models.SlugField(blank=True)
    description = models.TextField(blank=True)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True
    )
    price = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)]
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("shop", "title")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.shop.name})"


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="images"
    )
    image = CloudinaryField(
        'image',
        folder='vendoro/product_images',
        tags=['product_image'],
        blank=True,
        null=True
    )
    alt_text = models.CharField(max_length=200, blank=True)


class Inventory(models.Model):
    product = models.OneToOneField(
        Product, on_delete=models.CASCADE, related_name="inventory"
    )
    quantity = models.PositiveIntegerField(default=0)
    low_stock_threshold = models.PositiveIntegerField(default=5)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'inventories'

    def is_in_stock(self):
        return self.quantity > 0

    def is_low_stock(self):
        return self.quantity <= self.low_stock_threshold

    def __str__(self):
        return f"{self.product.title} ({self.quantity} in stock)"
