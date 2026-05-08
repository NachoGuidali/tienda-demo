from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.payments import views as payment_views
from apps.products import views as product_views

admin.site.site_header = 'Panel de Administración — VELO Store'
admin.site.site_title = 'VELO Store Admin'
admin.site.index_title = 'VELO Store'

urlpatterns = [
    path('admin/', admin.site.urls),

    # Tienda (template views)
    path('', product_views.store_index, name='store'),
    path('checkout/', product_views.store_checkout, name='checkout'),
    path('productos/<slug:slug>/', product_views.product_detail_page, name='product-detail'),
    path('pago-exitoso/', payment_views.pago_exitoso, name='pago_exitoso'),
    path('pago-pendiente/', payment_views.pago_pendiente, name='pago_pendiente'),
    path('pago-fallido/', payment_views.pago_fallido, name='pago_fallido'),

    # APIs
    path('api/products/', include('apps.products.urls')),
    path('api/orders/', include('apps.orders.urls')),
    path('api/mp/', include('apps.payments.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
