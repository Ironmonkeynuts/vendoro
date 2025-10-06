from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.urls import reverse
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
        base = (slugify(self.name) or "shop")
        # If user provided a slug, start from that; otherwise from base
        seed = (self.slug or base)
        # Try the given seed; if taken, append -1, -2, ...
        candidate = seed
        i = 1
        while Shop.objects.filter(slug=candidate).exclude(pk=self.pk).exists():
            candidate = f"{seed}-{i}"
            i += 1
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
        constraints = [
            models.UniqueConstraint(
                fields=["shop", "slug"],
                name="uniq_product_slug_per_shop"
            )
        ]

    def save(self, *args, **kwargs):
        """
        Ensure a unique, URL-friendly slug per shop.
        If a slug is provided, use it as the seed; otherwise slugify the title.
        Append -1, -2, ... until unique within this shop.
        """
        base = slugify(self.title) or "product"
        seed = self.slug or base

        candidate = seed
        i = 1
        # Uniqueness is per shop
        while Product.objects.filter(
                shop=self.shop, slug=candidate).exclude(pk=self.pk).exists():
            candidate = f"{seed}-{i}"
            i += 1

        self.slug = candidate
        return super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse(
            "marketplace:product_detail",
            kwargs={"shop_slug": self.shop.slug, "product_slug": self.slug}
        )

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


class ProductReview(models.Model):
    product = models.ForeignKey(
        "marketplace.Product",
        on_delete=models.CASCADE,
        related_name="reviews",
        null=True, blank=True,          # nullable for now
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="product_reviews",
        null=True, blank=True,          # nullable for now
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True, blank=True,          # nullable for now
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    is_public = models.BooleanField(default=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        u = getattr(self.user, "username", self.user_id)
        return f"Review({self.product_id}) by {u} • {self.rating}"


class ReviewReply(models.Model):
    review = models.OneToOneField(
        "marketplace.ProductReview",
        on_delete=models.CASCADE,
        related_name="reply",
    )
    responder = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="review_replies",
    )
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Reply to review {self.review_id}"
