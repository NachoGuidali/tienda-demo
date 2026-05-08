from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'active', 'product_count']
    list_editable = ['active']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']

    def product_count(self, obj):
        return obj.products.filter(active=True).count()
    product_count.short_description = 'Productos activos'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['thumbnail', 'name', 'category', 'price_display', 'stock', 'active', 'badge_display']
    list_display_links = ['thumbnail', 'name']
    list_editable = ['stock', 'active']
    list_filter = ['category', 'active', 'badge', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'thumbnail_large']
    fieldsets = (
        ('Información', {
            'fields': ('name', 'slug', 'category', 'description', 'badge'),
        }),
        ('Precios y stock', {
            'fields': ('price', 'original_price', 'stock', 'active'),
        }),
        ('Imagen y colores', {
            'fields': ('thumbnail_large', 'image', 'swatches'),
        }),
        ('Metadatos', {
            'fields': ('created_at',),
            'classes': ('collapse',),
        }),
    )

    def thumbnail(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width:48px;height:60px;object-fit:cover;border-radius:3px;" />',
                obj.image.url
            )
        return format_html(
            '<div style="width:48px;height:60px;background:#ecebe5;border-radius:3px;'
            'display:grid;place-items:center;font-size:9px;color:#999;">SIN IMG</div>'
        )
    thumbnail.short_description = ''

    def thumbnail_large(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width:200px;border-radius:4px;" />', obj.image.url
            )
        return '—'
    thumbnail_large.short_description = 'Vista previa'

    def price_display(self, obj):
        if obj.original_price:
            return format_html(
                '<span style="text-decoration:line-through;color:#999;font-size:11px;">'
                '${}</span>&nbsp;<strong>${}</strong>',
                f'{obj.original_price:,.0f}', f'{obj.price:,.0f}'
            )
        return format_html('<strong>${}</strong>', f'{obj.price:,.0f}')
    price_display.short_description = 'Precio'
    price_display.admin_order_field = 'price'

    def badge_display(self, obj):
        colors = {'new': '#0b0b0b', 'sale': '#e07a3c', '': '#ccc'}
        labels = {'new': 'NUEVO', 'sale': 'SALE', '': '—'}
        color = colors.get(obj.badge, '#ccc')
        label = labels.get(obj.badge, obj.badge)
        if not obj.badge:
            return format_html('<span style="color:#ccc">—</span>')
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;border-radius:2px;'
            'font-size:10px;font-weight:700;letter-spacing:0.1em">{}</span>',
            color, label
        )
    badge_display.short_description = 'Badge'
