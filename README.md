# VELO Store — Backend Django

Tienda ecommerce completa con Django 4.2, DRF, Mercado Pago Checkout Pro y Django Admin personalizado.

---

## Stack

| Capa | Tecnología |
|---|---|
| Backend | Python 3.11+ / Django 4.2 |
| API | Django REST Framework |
| Pagos | Mercado Pago Checkout Pro |
| DB (dev) | SQLite |
| DB (prod) | PostgreSQL (via `DATABASE_URL`) |
| Imágenes | Pillow |
| Static (prod) | WhiteNoise |

---

## Instalación rápida

### 1. Clonar e instalar

```bash
git clone <repo>
cd tienda-venta
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configurar `.env`

```bash
cp .env.example .env
# Editá .env con tus credenciales de Mercado Pago
```

Variables clave:

```env
SECRET_KEY=django-insecure-cambia-esto
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
MP_ACCESS_TOKEN=TEST-xxxx
MP_PUBLIC_KEY=TEST-xxxx
BASE_URL=http://localhost:8000
```

### 3. Migrar base de datos

```bash
python manage.py migrate
```

### 4. Cargar datos de prueba

```bash
python manage.py seed_products
```

Crea 3 categorías, 12 productos y el superusuario `admin / admin123`.

### 5. Correr servidor

```bash
python manage.py runserver
```

- Tienda: http://localhost:8000/
- Admin: http://localhost:8000/admin/

---

## Credenciales de Mercado Pago

### Sandbox (pruebas)

1. Entrá a https://www.mercadopago.com.ar/developers
2. Login con tu cuenta de MP
3. Ir a **Tus integraciones → Crear aplicación**
4. Luego en la app: **Credenciales de prueba**
5. Copiá `Access token` y `Public key` al `.env`

Con `DEBUG=True`, el checkout usa `sandbox_init_point` automáticamente.

**Tarjetas de prueba de MP:**

| Tarjeta | Nro | CVV | Resultado |
|---|---|---|---|
| Visa | 4509 9535 6623 3704 | 123 | Aprobado |
| Mastercard | 5031 7557 3453 0604 | 123 | Aprobado |
| Visa | 4000 0000 0000 0002 | 123 | Rechazado |

### Producción

1. En el panel de MP: **Credenciales de producción**
2. Poner `DEBUG=False` en `.env`
3. Cambiar `BASE_URL` a tu dominio real (necesario para webhooks)

---

## Estructura del proyecto

```
tienda-venta/
├── manage.py
├── requirements.txt
├── .env.example
├── tienda/
│   ├── settings.py       ← configuración principal
│   └── urls.py           ← URLs raíz
├── apps/
│   ├── products/         ← modelos, API y admin de productos
│   ├── orders/           ← checkout y órdenes
│   └── payments/         ← webhook MP, páginas de resultado
├── templates/
│   ├── admin/            ← personalización del admin Django
│   └── store/            ← tienda + páginas de pago
└── static/
    └── css/admin_custom.css
```

---

## URLs

| URL | Descripción |
|---|---|
| `/` | Tienda (SPA con productos cargados desde API) |
| `/checkout/` | Formulario de checkout (alternativo al modal) |
| `/pago-exitoso/` | Resultado exitoso de MP |
| `/pago-pendiente/` | Pago pendiente |
| `/pago-fallido/` | Pago rechazado |
| `/admin/` | Panel de administración |
| `/api/products/` | Lista de productos activos |
| `/api/products/<slug>/` | Detalle de producto |
| `/api/orders/checkout/` | Crear orden + preference MP |
| `/api/mp/webhook/` | Webhook de Mercado Pago |

---

## Flujo de pago

```
Usuario llena form → POST /api/orders/checkout/
  → crea Order (status=pending)
  → crea MP Preference
  → devuelve { init_point }
→ JS redirige a MP
→ Usuario paga en MP
→ MP llama /api/mp/webhook/ → Order.status = 'paid' + emails
→ MP redirige a /pago-exitoso/
```

---

## Deploy en Railway

```bash
# Instalar Railway CLI
npm i -g @railway/cli
railway login
railway init

# Variables de entorno en Railway dashboard:
# SECRET_KEY, DEBUG=False, DATABASE_URL (PostgreSQL), MP_ACCESS_TOKEN, etc.

# Agregar al proyecto
railway up
```

**Procfile** (crear si no existe):
```
web: gunicorn tienda.wsgi --log-file -
```

**collectstatic** (Railway lo ejecuta automáticamente si configurás el build command):
```bash
python manage.py collectstatic --noinput
```

## Deploy en Render

1. Nuevo servicio Web → conectar repo
2. Build command: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
3. Start command: `gunicorn tienda.wsgi`
4. Variables de entorno: igual que `.env.example`
5. Agregar PostgreSQL desde Render dashboard → copiar `DATABASE_URL`

---

## Django Admin

Accedé a `/admin/` con `admin / admin123`.

**Funcionalidades:**
- **Productos**: thumbnail inline, precio editable en lista, filtros por categoría/badge
- **Órdenes**: ver items formateados, cambiar estado, exportar CSV, marcar como enviado
- **Categorías**: gestión simple

---

## Agregar productos con imagen

En el admin, editá un producto y subí una imagen. La tienda la muestra automáticamente en lugar del gradiente placeholder.
# tienda-demo
