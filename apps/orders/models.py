from django.db import models


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('paid', 'Pagado'),
        ('shipped', 'Enviado'),
        ('cancelled', 'Cancelado'),
    ]

    mp_payment_id = models.CharField(max_length=200, blank=True, null=True)
    mp_preference_id = models.CharField(max_length=200, blank=True, null=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Estado'
    )
    customer_name = models.CharField(max_length=200, verbose_name='Nombre')
    customer_email = models.EmailField(verbose_name='Email')
    customer_phone = models.CharField(max_length=50, blank=True, verbose_name='Teléfono')
    shipping_address = models.JSONField(verbose_name='Dirección de envío')
    items = models.JSONField(verbose_name='Productos')
    total = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Total')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Orden'
        verbose_name_plural = 'Órdenes'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.order_number()} — {self.customer_name}'

    def order_number(self):
        return f'VS-{self.id:06d}'
