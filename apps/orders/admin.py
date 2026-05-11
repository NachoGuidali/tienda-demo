import csv
from django.contrib import admin
from django.http import HttpResponse
from django.utils.html import format_html
from .models import Order


def export_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="ordenes.csv"'
    response.write('﻿')  # BOM para Excel
    writer = csv.writer(response)
    writer.writerow(['Nº Orden', 'Cliente', 'Email', 'Teléfono', 'Total', 'Estado', 'Fecha'])
    for order in queryset:
        writer.writerow([
            order.order_number(),
            order.customer_name,
            order.customer_email,
            order.customer_phone,
            f'${float(order.total):,.0f}',
            order.get_status_display(),
            order.created_at.strftime('%Y-%m-%d %H:%M'),
        ])
    return response
export_csv.short_description = 'Exportar CSV'


def mark_shipped(modeladmin, request, queryset):
    updated = queryset.filter(status='paid').update(status='shipped')
    modeladmin.message_user(request, f'{updated} orden(es) marcada(s) como enviada(s).')
mark_shipped.short_description = 'Marcar como enviado'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'order_number_col', 'customer_name', 'customer_email',
        'total_display', 'status', 'created_at',
    ]
    list_display_links = ['order_number_col', 'customer_name']
    list_editable = ['status']
    list_filter = ['status', 'created_at']
    search_fields = ['customer_name', 'customer_email', 'mp_payment_id']
    readonly_fields = [
        'order_number_col', 'customer_name', 'customer_email', 'customer_phone',
        'address_display', 'items_display', 'total', 'mp_payment_id',
        'mp_preference_id', 'created_at', 'updated_at',
    ]
    actions = [mark_shipped, export_csv]
    fieldsets = (
        ('Cliente', {
            'fields': ('customer_name', 'customer_email', 'customer_phone', 'address_display'),
        }),
        ('Pedido', {
            'fields': ('items_display', 'total', 'status'),
        }),
        ('Mercado Pago', {
            'fields': ('mp_payment_id', 'mp_preference_id'),
            'classes': ('collapse',),
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def order_number_col(self, obj):
        return obj.order_number()
    order_number_col.short_description = 'Orden'

    def total_display(self, obj):
        return format_html('<strong>${}</strong>', f'{float(obj.total):,.0f}')
    total_display.short_description = 'Total'
    total_display.admin_order_field = 'total'

    def address_display(self, obj):
        addr = obj.shipping_address
        if not addr:
            return '—'
        return format_html(
            '<span>{} {}, {} {} — {}</span>',
            addr.get('calle', ''),
            addr.get('numero', ''),
            addr.get('ciudad', ''),
            addr.get('provincia', ''),
            addr.get('cp', ''),
        )
    address_display.short_description = 'Dirección'

    def items_display(self, obj):
        if not obj.items:
            return '—'
        rows = ''.join(
            f'<tr>'
            f'<td style="padding:6px 12px 6px 0">{i.get("name","")}</td>'
            f'<td style="padding:6px 12px 6px 0;text-align:center">×{i.get("qty",1)}</td>'
            f'<td style="padding:6px 0;text-align:right;font-family:monospace">'
            f'${float(i.get("price",0)):,.0f}</td>'
            f'</tr>'
            for i in obj.items
        )
        subtotal = sum(float(i.get('price', 0)) * i.get('qty', 1) for i in obj.items)
        return format_html(
            '<table style="width:100%;border-collapse:collapse;font-size:13px">'
            '<thead><tr>'
            '<th style="text-align:left;padding:0 12px 8px 0;border-bottom:1px solid #eee">Producto</th>'
            '<th style="padding:0 12px 8px 0;border-bottom:1px solid #eee">Cant.</th>'
            '<th style="text-align:right;padding:0 0 8px 0;border-bottom:1px solid #eee">Precio</th>'
            '</tr></thead>'
            '<tbody>{}</tbody>'
            '<tfoot><tr>'
            '<td colspan="2" style="padding-top:8px;border-top:1px solid #eee"><strong>Subtotal</strong></td>'
            '<td style="padding-top:8px;border-top:1px solid #eee;text-align:right;font-family:monospace">'
            '<strong>${}</strong></td>'
            '</tr></tfoot>'
            '</table>',
            rows, f'{subtotal:,.0f}'
        )
    items_display.short_description = 'Productos del pedido'
