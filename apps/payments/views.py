import json
import logging
import mercadopago
from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from apps.orders.models import Order

logger = logging.getLogger(__name__)


@csrf_exempt
def webhook(request):
    """Recibe notificaciones de Mercado Pago y actualiza el estado de la orden."""
    if request.method != 'POST':
        return HttpResponse(status=405)

    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, Exception):
        data = {}

    # MP puede mandar el tipo en el body o como query param
    notification_type = data.get('type') or request.GET.get('type')

    if notification_type == 'payment':
        payment_id = (
            data.get('data', {}).get('id')
            or request.GET.get('data.id')
            or request.GET.get('id')
        )
        if payment_id:
            _process_payment(str(payment_id))

    return HttpResponse(status=200)


def _process_payment(payment_id: str):
    sdk = mercadopago.SDK(settings.MP_ACCESS_TOKEN)
    result = sdk.payment().get(payment_id)

    if result.get('status') != 200:
        logger.warning('MP payment fetch failed (id=%s): %s', payment_id, result)
        return

    payment = result['response']
    mp_status = payment.get('status')
    external_ref = payment.get('external_reference')

    if not external_ref:
        return

    try:
        order = Order.objects.get(id=int(external_ref))
    except (Order.DoesNotExist, ValueError):
        logger.warning('Order not found for external_reference=%s', external_ref)
        return

    order.mp_payment_id = payment_id

    if mp_status == 'approved':
        order.status = 'paid'
        order.save(update_fields=['mp_payment_id', 'status'])
        _send_confirmation_emails(order)
    elif mp_status in ('cancelled', 'rejected'):
        order.status = 'cancelled'
        order.save(update_fields=['mp_payment_id', 'status'])
    else:
        order.save(update_fields=['mp_payment_id'])


def _send_confirmation_emails(order: Order):
    items_text = '\n'.join(
        f"  · {i['name']} ×{i['qty']} = ${float(i['price']):,.0f}"
        for i in order.items
    )
    addr = order.shipping_address
    addr_text = (
        f"{addr.get('calle','')} {addr.get('numero','')}, "
        f"{addr.get('ciudad','')} {addr.get('provincia','')} — CP {addr.get('cp','')}"
    )

    # Email al cliente
    try:
        send_mail(
            subject=f'¡Tu pedido {order.order_number()} fue confirmado! — VELO Store',
            message=(
                f'¡Hola {order.customer_name}!\n\n'
                f'Tu pedido {order.order_number()} fue confirmado con éxito.\n\n'
                f'Productos:\n{items_text}\n\n'
                f'Total: ${float(order.total):,.0f}\n'
                f'Envío a: {addr_text}\n\n'
                f'Te avisamos cuando tu pedido esté en camino.\n\n'
                f'¡Gracias por comprar en VELO Store!'
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.customer_email],
            fail_silently=True,
        )
    except Exception as exc:
        logger.error('Error sending customer email for order %s: %s', order.id, exc)

    # Email al admin
    try:
        send_mail(
            subject=f'Nueva venta: {order.order_number()} — ${float(order.total):,.0f}',
            message=(
                f'Nueva venta confirmada.\n\n'
                f'Orden: {order.order_number()}\n'
                f'Cliente: {order.customer_name} <{order.customer_email}>\n'
                f'Teléfono: {order.customer_phone or "—"}\n'
                f'Envío a: {addr_text}\n\n'
                f'Productos:\n{items_text}\n\n'
                f'Total: ${float(order.total):,.0f}\n'
                f'MP Payment ID: {order.mp_payment_id}'
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.ADMIN_EMAIL],
            fail_silently=True,
        )
    except Exception as exc:
        logger.error('Error sending admin email for order %s: %s', order.id, exc)


def pago_exitoso(request):
    external_ref = request.GET.get('external_reference')
    order = None
    if external_ref:
        try:
            order = Order.objects.get(id=int(external_ref))
        except (Order.DoesNotExist, ValueError):
            pass
    return render(request, 'store/pago_exitoso.html', {'order': order})


def pago_pendiente(request):
    return render(request, 'store/pago_pendiente.html')


def pago_fallido(request):
    return render(request, 'store/pago_fallido.html')
