from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name='Nombre')
    slug = models.SlugField(unique=True)
    active = models.BooleanField(default=True, verbose_name='Activa')

    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(models.Model):
    BADGE_CHOICES = [
        ('', 'Sin badge'),
        ('new', 'Nuevo'),
        ('sale', 'Sale'),
    ]

    name = models.CharField(max_length=200, verbose_name='Nombre')
    slug = models.SlugField(unique=True)
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT,
        related_name='products', verbose_name='Categoría'
    )
    description = models.TextField(blank=True, verbose_name='Descripción')
    price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Precio')
    original_price = models.DecimalField(
        max_digits=12, decimal_places=2,
        null=True, blank=True, verbose_name='Precio original'
    )
    stock = models.PositiveIntegerField(default=0, verbose_name='Stock')
    active = models.BooleanField(default=True, verbose_name='Activo')
    badge = models.CharField(
        max_length=10, choices=BADGE_CHOICES,
        default='', blank=True, verbose_name='Badge'
    )
    swatches = models.JSONField(default=list, blank=True, verbose_name='Colores (hex)')
    sizes = models.JSONField(default=list, blank=True, verbose_name='Talles disponibles')
    colors = models.JSONField(default=list, blank=True, verbose_name='Colores detallados')
    features = models.JSONField(default=list, blank=True, verbose_name='Características')
    image = models.ImageField(
        upload_to='products/', null=True, blank=True, verbose_name='Imagen'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
