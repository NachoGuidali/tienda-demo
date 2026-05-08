import logging
import mercadopago
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from apps.products.models import Product
from .models import Order

logger = logging.getLogger(__name__)


@api_view(['POST'])
def checkout(request):
    """
    Recibe los items del carrito + datos del cliente,
    crea la Order y la preference de Mercado Pago.
    Devuelve init_point para redirigir al usuario a MP.
    """
    data = request.data
    raw_items = data.get('items', [])

    if not raw_items:
        return Response({'error': 'El carrito está vacío.'}, status=400)

    # Revalidar precios desde la base de datos (no confiar en el cliente)
    validated_items = []
    total = 0
    for item in raw_items:
        try:
            product = Product.objects.get(id=item['id'], active=True)
        except (Product.DoesNotExist, KeyError):
            return Response({'error': f"Producto #{item.get('id')} no disponible."}, status=400)

        try:
            qty = max(1, int(item['qty']))
        except (KeyError, ValueError):
            qty = 1

        price = float(product.price)
        total += price * qty
        validated_items.append({
            'id': product.id,
            'name': product.name,
            'price': price,
            'qty': qty,
        })

    # Crear la orden con status pending
    order = Order.objects.create(
        customer_name=data.get('customer_name', ''),
        customer_email=data.get('customer_email', ''),
        customer_phone=data.get('customer_phone', ''),
        shipping_address=data.get('shipping_address', {}),
        items=validated_items,
        total=total,
        status='pending',
    )

    # Crear preference en Mercado Pago
    sdk = mercadopago.SDK(settings.MP_ACCESS_TOKEN)
    mp_items = [
        {
            'id': str(i['id']),
            'title': i['name'],
            'quantity': i['qty'],
            'unit_price': i['price'],
            'currency_id': 'ARS',
        }
        for i in validated_items
    ]

    preference_data = {
        'items': mp_items,
        'payer': {
            'name': order.customer_name,
            'email': order.customer_email,
        },
        'back_urls': {
            'success': f'{settings.BASE_URL}/pago-exitoso/',
            'failure': f'{settings.BASE_URL}/pago-fallido/',
            'pending': f'{settings.BASE_URL}/pago-pendiente/',
        },
        'auto_return': 'approved',
        'notification_url': f'{settings.BASE_URL}/api/mp/webhook/',
        'external_reference': str(order.id),
        'statement_descriptor': 'VELO Store',
    }

    result = sdk.preference().create(preference_data)

    if result.get('status') == 201:
        preference = result['response']
        order.mp_preference_id = preference.get('id')
        order.save(update_fields=['mp_preference_id'])

        # Sandbox en DEBUG, producción en producción
        init_point = (
            preference.get('sandbox_init_point')
            if settings.DEBUG
            else preference.get('init_point')
        )
        return Response({
            'order_id': order.id,
            'order_number': order.order_number(),
            'init_point': init_point,
        })

    # Si MP falla, cancela la orden para no dejar basura
    logger.error('MP preference error (order=%s): %s', order.id, result)
    order.status = 'cancelled'
    order.save(update_fields=['status'])
    return Response({'error': 'Error al conectar con Mercado Pago. Intentá nuevamente.'}, status=502)
