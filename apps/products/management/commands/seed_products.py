from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from apps.products.models import Category, Product


CATEGORIES = [
    {'name': 'Hombre', 'slug': 'hombre'},
    {'name': 'Mujer', 'slug': 'mujer'},
    {'name': 'Niños', 'slug': 'ninos'},
]

PRODUCTS = [
    {
        'name': 'Aero 01 Runner',
        'category': 'hombre',
        'price': 119000,
        'badge': 'new',
        'stock': 15,
        'description': 'Zapatilla running de entrada de línea. Suela EVA de alta densidad, malla técnica transpirable con refuerzos laterales. Ideal para entrenamiento diario en asfalto o pista.',
        'swatches': ['#ffffff', '#1a1a1a', '#d4cdb8'],
        'sizes': ['36', '37', '38', '39', '40', '41', '42', '43'],
        'colors': [
            {'name': 'Blanco', 'hex': '#ffffff'},
            {'name': 'Negro', 'hex': '#1a1a1a'},
            {'name': 'Crema', 'hex': '#d4cdb8'},
        ],
        'features': [
            {'label': 'Material superior', 'value': 'Malla técnica transpirable'},
            {'label': 'Suela', 'value': 'EVA de alta densidad'},
            {'label': 'Peso', 'value': '210g (talle 41)'},
            {'label': 'Cierre', 'value': 'Cordones planos encerados'},
            {'label': 'Origen', 'value': 'Diseñado en Buenos Aires'},
        ],
    },
    {
        'name': 'Aero 03 Performance',
        'category': 'hombre',
        'price': 129000,
        'badge': 'new',
        'stock': 10,
        'description': 'Nuestra zapatilla más liviana hasta la fecha. Suela de espuma reactiva, malla técnica de doble capa y sistema de amarre que se ajusta al pie en segundos. Diseñada con corredores reales en Palermo.',
        'swatches': ['#1a1a1a', '#0b0b0b', '#5a4a30'],
        'sizes': ['37', '38', '39', '40', '41', '42', '43', '44'],
        'colors': [
            {'name': 'Negro', 'hex': '#1a1a1a'},
            {'name': 'Carbón', 'hex': '#2a2a2a'},
            {'name': 'Khaki', 'hex': '#5a4a30'},
        ],
        'features': [
            {'label': 'Material superior', 'value': 'Malla técnica doble capa'},
            {'label': 'Suela', 'value': 'Espuma reactiva ZeroFoam'},
            {'label': 'Peso', 'value': '187g (talle 41)'},
            {'label': 'Drop', 'value': '22mm'},
            {'label': 'Cierre', 'value': 'Sistema Flylock'},
            {'label': 'Origen', 'value': 'Diseñado en Buenos Aires'},
        ],
    },
    {
        'name': 'Solar Mid Boot',
        'category': 'mujer',
        'price': 145000,
        'original_price': 180000,
        'badge': 'sale',
        'stock': 8,
        'description': 'Bota media de cuero sintético premium. Suela de goma vulcanizada con textura, forro interior de algodón. Un ícono de temporada.',
        'swatches': ['#f4a93a', '#0b0b0b'],
        'sizes': ['35', '36', '37', '38', '39', '40'],
        'colors': [
            {'name': 'Naranja', 'hex': '#f4a93a'},
            {'name': 'Negro', 'hex': '#0b0b0b'},
        ],
        'features': [
            {'label': 'Material', 'value': 'Cuero sintético premium'},
            {'label': 'Forro', 'value': 'Algodón 100%'},
            {'label': 'Suela', 'value': 'Goma vulcanizada'},
            {'label': 'Cierre', 'value': 'Cremallera lateral YKK'},
            {'label': 'Caño', 'value': 'Mid (cubre tobillo)'},
        ],
    },
    {
        'name': 'Field Jacket Tan',
        'category': 'hombre',
        'price': 89000,
        'badge': '',
        'stock': 20,
        'description': 'Campera field clásica en tono tan. Cuatro bolsillos con solapa, cierre YKK resistente al agua. Revestimiento interior de microfibra para días frescos.',
        'swatches': ['#8c6a4a', '#1a1a1a', '#3a2417'],
        'sizes': ['S', 'M', 'L', 'XL', 'XXL'],
        'colors': [
            {'name': 'Tan', 'hex': '#8c6a4a'},
            {'name': 'Negro', 'hex': '#1a1a1a'},
            {'name': 'Marrón oscuro', 'hex': '#3a2417'},
        ],
        'features': [
            {'label': 'Exterior', 'value': 'Nylon ripstop resistente al agua'},
            {'label': 'Interior', 'value': 'Microfibra'},
            {'label': 'Cierre', 'value': 'YKK resistente al agua'},
            {'label': 'Bolsillos', 'value': '4 con solapa'},
            {'label': 'Cuidado', 'value': 'Lavar a 30°C, no secar en secadora'},
        ],
    },
    {
        'name': 'Glacier Knit Crew',
        'category': 'mujer',
        'price': 65000,
        'badge': '',
        'stock': 25,
        'description': 'Buzo de punto en algodón reciclado. Corte recto, cuello redondo ribeteado. La prenda que nunca falta en el guardarropa de temporada.',
        'swatches': ['#6a9bd1', '#ffffff', '#1d3556'],
        'sizes': ['XS', 'S', 'M', 'L', 'XL'],
        'colors': [
            {'name': 'Azul glaciar', 'hex': '#6a9bd1'},
            {'name': 'Blanco', 'hex': '#ffffff'},
            {'name': 'Azul marino', 'hex': '#1d3556'},
        ],
        'features': [
            {'label': 'Material', 'value': '80% algodón reciclado, 20% poliéster'},
            {'label': 'Corte', 'value': 'Recto / Regular fit'},
            {'label': 'Cuello', 'value': 'Redondo con ribete'},
            {'label': 'Cuidado', 'value': 'Lavar a mano o ciclo delicado'},
        ],
    },
    {
        'name': 'Linen Trouser Wide',
        'category': 'mujer',
        'price': 78000,
        'badge': 'new',
        'stock': 12,
        'description': 'Pantalón ancho de lino puro. Cintura elástica con lazo, dos bolsillos laterales con vivo. Fresco y versátil para el día a día.',
        'swatches': ['#d4cdb8', '#1a1a1a', '#807358'],
        'sizes': ['XS', 'S', 'M', 'L', 'XL'],
        'colors': [
            {'name': 'Arena', 'hex': '#d4cdb8'},
            {'name': 'Negro', 'hex': '#1a1a1a'},
            {'name': 'Oliva', 'hex': '#807358'},
        ],
        'features': [
            {'label': 'Material', 'value': '100% lino'},
            {'label': 'Corte', 'value': 'Wide leg / Pierna ancha'},
            {'label': 'Cintura', 'value': 'Elástica con lazo'},
            {'label': 'Bolsillos', 'value': '2 laterales con vivo'},
            {'label': 'Cuidado', 'value': 'Lavar a 30°C, no secar a máquina'},
        ],
    },
    {
        'name': 'Volley Tee Coral',
        'category': 'mujer',
        'price': 49000,
        'original_price': 75000,
        'badge': 'sale',
        'stock': 30,
        'description': 'Remera oversize de algodón 100%. Teñido en prenda para lograr un efecto vintage natural. Detalles bordados en el pecho izquierdo.',
        'swatches': ['#e08a7c', '#ffffff', '#1a1a1a'],
        'sizes': ['XS', 'S', 'M', 'L', 'XL', 'XXL'],
        'colors': [
            {'name': 'Coral', 'hex': '#e08a7c'},
            {'name': 'Blanco', 'hex': '#ffffff'},
            {'name': 'Negro', 'hex': '#1a1a1a'},
        ],
        'features': [
            {'label': 'Material', 'value': '100% algodón'},
            {'label': 'Corte', 'value': 'Oversize'},
            {'label': 'Teñido', 'value': 'Garment dye (efecto vintage)'},
            {'label': 'Detalle', 'value': 'Bordado en pecho izquierdo'},
        ],
    },
    {
        'name': 'Stealth Hoodie Pro',
        'category': 'hombre',
        'price': 92000,
        'badge': '',
        'stock': 18,
        'description': 'Hoodie técnico anti-pilling con interior cepillado. Bolsillo canguro, capucha ajustable con cordón plano. La prenda favorita para entrenar o salir.',
        'swatches': ['#2a2a2a', '#ffffff', '#807358'],
        'sizes': ['S', 'M', 'L', 'XL', 'XXL'],
        'colors': [
            {'name': 'Carbón', 'hex': '#2a2a2a'},
            {'name': 'Blanco', 'hex': '#ffffff'},
            {'name': 'Oliva', 'hex': '#807358'},
        ],
        'features': [
            {'label': 'Material exterior', 'value': '80% algodón, 20% poliéster'},
            {'label': 'Interior', 'value': 'Polar cepillado anti-pilling'},
            {'label': 'Bolsillos', 'value': 'Canguro + 2 laterales ocultos'},
            {'label': 'Capucha', 'value': 'Ajustable con cordón plano'},
            {'label': 'Cuidado', 'value': 'Lavar a 30°C, no planchar capucha'},
        ],
    },
    {
        'name': 'Court 02 Mini',
        'category': 'ninos',
        'price': 65000,
        'badge': 'new',
        'stock': 22,
        'description': 'Zapatilla court clásica para niños. Suela de goma flexible para el movimiento natural, cierre velcro para independencia. Diseñada para durar.',
        'swatches': ['#7ea35a', '#ffffff', '#1a1a1a'],
        'sizes': ['28', '29', '30', '31', '32', '33', '34', '35', '36'],
        'colors': [
            {'name': 'Verde bosque', 'hex': '#7ea35a'},
            {'name': 'Blanco', 'hex': '#ffffff'},
            {'name': 'Negro', 'hex': '#1a1a1a'},
        ],
        'features': [
            {'label': 'Material', 'value': 'Canvas + suela de goma'},
            {'label': 'Cierre', 'value': 'Velcro (sin cordones)'},
            {'label': 'Suela', 'value': 'Goma flexible antideslizante'},
            {'label': 'Edad recomendada', 'value': '3 a 12 años'},
        ],
    },
    {
        'name': 'Velo Backpack 24L',
        'category': 'hombre',
        'price': 89000,
        'original_price': 129000,
        'badge': 'sale',
        'stock': 7,
        'description': 'Mochila 24L de tela ripstop resistente al agua. Compartimiento acolchado para laptop de hasta 15", bolsillos organizadores y asa lateral reforzada.',
        'swatches': ['#e07a3c', '#1a1a1a'],
        'sizes': ['Único'],
        'colors': [
            {'name': 'Naranja', 'hex': '#e07a3c'},
            {'name': 'Negro', 'hex': '#1a1a1a'},
        ],
        'features': [
            {'label': 'Capacidad', 'value': '24 litros'},
            {'label': 'Material', 'value': 'Nylon ripstop 420D'},
            {'label': 'Laptop', 'value': 'Compartimiento hasta 15"'},
            {'label': 'Correas', 'value': 'Acolchadas y ajustables'},
            {'label': 'Medidas', 'value': '48 × 30 × 18 cm'},
        ],
    },
    {
        'name': 'Pique Polo Sand',
        'category': 'hombre',
        'price': 55000,
        'badge': '',
        'stock': 35,
        'description': 'Polo de piqué algodón pima. Corte slim, tres botones nácar y logo bordado en pecho izquierdo. Clásico y refinado para cualquier ocasión.',
        'swatches': ['#d4cdb8', '#1a1a1a', '#5a4a30'],
        'sizes': ['S', 'M', 'L', 'XL', 'XXL'],
        'colors': [
            {'name': 'Arena', 'hex': '#d4cdb8'},
            {'name': 'Negro', 'hex': '#1a1a1a'},
            {'name': 'Marrón', 'hex': '#5a4a30'},
        ],
        'features': [
            {'label': 'Material', 'value': '100% algodón pima'},
            {'label': 'Tejido', 'value': 'Piqué'},
            {'label': 'Corte', 'value': 'Slim fit'},
            {'label': 'Botones', 'value': '3 botones nácar'},
            {'label': 'Cuidado', 'value': 'Lavar a 30°C, planchar a temperatura media'},
        ],
    },
    {
        'name': 'Mini Bomber Lila',
        'category': 'ninos',
        'price': 72000,
        'badge': 'new',
        'stock': 14,
        'description': 'Campera bomber para niños en tono lila. Puños y cintura elásticos, cierre central, dos bolsillos laterales. Liviana y cómoda para el día a día.',
        'swatches': ['#7a5f9b', '#ffffff', '#2c1e44'],
        'sizes': ['4', '6', '8', '10', '12', '14'],
        'colors': [
            {'name': 'Lila', 'hex': '#7a5f9b'},
            {'name': 'Blanco', 'hex': '#ffffff'},
            {'name': 'Morado oscuro', 'hex': '#2c1e44'},
        ],
        'features': [
            {'label': 'Material', 'value': 'Poliéster ripstop'},
            {'label': 'Forro', 'value': 'Seda (100% poliéster)'},
            {'label': 'Puños', 'value': 'Elástico acanalado'},
            {'label': 'Cierre', 'value': 'YKK frontal'},
            {'label': 'Talle (años)', 'value': '4 a 14 años'},
        ],
    },
]


class Command(BaseCommand):
    help = 'Crea categorías, productos de ejemplo y el superusuario admin/admin123'

    def handle(self, *args, **options):
        # Superusuario
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@velo.store', 'admin123')
            self.stdout.write(self.style.SUCCESS('✓ Superusuario creado: admin / admin123'))
        else:
            self.stdout.write('  Superusuario admin ya existe, omitiendo.')

        # Categorías
        cats = {}
        for cat_data in CATEGORIES:
            cat, created = Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults={'name': cat_data['name'], 'active': True},
            )
            cats[cat_data['slug']] = cat
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Categoría: {cat.name}'))

        # Productos
        created_count = 0
        updated_count = 0
        for p_data in PRODUCTS:
            cat_slug = p_data.pop('category')
            slug = slugify(p_data['name'])

            obj, created = Product.objects.get_or_create(
                slug=slug,
                defaults={'category': cats[cat_slug], **p_data},
            )
            if not created:
                # Update existing products with new fields (sizes, colors, features)
                for field in ('sizes', 'colors', 'features', 'description'):
                    if field in p_data:
                        setattr(obj, field, p_data[field])
                obj.save()
                updated_count += 1
            else:
                created_count += 1

            p_data['category'] = cat_slug  # restore for idempotency

        self.stdout.write(
            self.style.SUCCESS(
                f'✓ {created_count} producto(s) creado(s), {updated_count} actualizado(s).'
            )
        )
        self.stdout.write(self.style.SUCCESS('\n¡Listo! Ejecutá: python manage.py runserver'))
