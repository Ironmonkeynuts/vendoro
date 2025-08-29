from django.conf import settings
from django.db import models
from django.utils.text import slugify


User = settings.AUTH_USER_MODEL


class Shop(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shops')
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    tagline = models.CharField(max_length=255, blank=True)
    primary_color = models.CharField(max_length=7, default='#111827')
    highlight_color = models.CharField(max_length=7, default='#06b6d4')
    banner = models.ImageField(upload_to='shop_banners/', blank=True)

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
