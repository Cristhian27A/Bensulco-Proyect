"""Crea datos de ejemplo para el catálogo de productos.

    python manage.py seed_catalogo

Genera categorías, productos y clientes B2B de ejemplo para probar
el sistema de pedidos.
"""

from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from catalogo.models import Categoria, ClienteB2B, LineaPedidoB2B, PedidoB2B, Producto

D = Decimal


class Command(BaseCommand):
    help = "Carga datos de ejemplo para el catálogo de productos y clientes B2B."

    def add_arguments(self, parser):
        parser.add_argument(
            "--borrar",
            action="store_true",
            help="Borra los datos existentes antes de crear los nuevos. ¡PELIGROSO! Esto eliminará productos reales.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options["borrar"]:
            self.stdout.write(
                self.style.WARNING(
                    "⚠️  ADVERTENCIA: Está a punto de borrar TODOS los productos, categorías y pedidos."
                )
            )
            self.stdout.write("Los datos reales se perderán permanentemente.")
            self.stdout.write("Si desea continuar, use --borrar-confirm en lugar de --borrar")
            return

        # Si solo queremos agregar sin borrar (comportamiento seguro por defecto)
        # Crear categorías (si no existen)
        categorias_datos = [
            "Bolsas Herméticas",
            "Papeles Aluminio",
            "Bolsas Negras- Blancas",
            "Cubiertos",
            "Bwol",
            "platos",
            "vasos",
            "Cartucho transparente",
            "Media caja",
        ]

        categorias = {}
        for nombre in categorias_datos:
            categoria, created = Categoria.objects.get_or_create(nombre=nombre)
            categorias[nombre] = categoria
            if created:
                self.stdout.write(f"Categoría creada: {nombre}")
            else:
                self.stdout.write(f"Categoría ya existe: {nombre}")

        # Crear productos solo si no existen (por defecto seguro)
        productos_datos = [
            # (categoria, nombre, sku, descripcion, precio_caja, precio_media_caja, precio_unidad, precio_consumidor, unidades_por_caja, permite_media_caja, aplica_itbms, codigo_barras)
            ("Bolsas Herméticas", "Bolsa Hermética 8x10", "BH-001", "Bolsa hermética 8x10 pulgadas", D("45.00"), D("22.50"), D("0.75"), D("0.80"), 60, True, True, "7 595288 000001"),
            ("Bolsas Herméticas", "Bolsa Hermética 10x12", "BH-002", "Bolsa hermética 10x12 pulgadas", D("52.00"), D("26.00"), D("0.87"), D("0.95"), 60, True, True, "7 595288 000002"),
            ("Papeles Aluminio", "Papel Aluminio 40cm", "PA-001", "Papel aluminio 40cm ancho", D("38.00"), D("19.00"), D("0.63"), D("0.70"), 60, True, True, "7 595288 000003"),
            ("Papeles Aluminio", "Papel Aluminio 45cm", "PA-002", "Papel aluminio 45cm ancho", D("42.00"), D("21.00"), D("0.70"), D("0.75"), 60, False, True, "7 595288 000004"),
            ("Bolsas Negras- Blancas", "Bolsa Negra Mediana", "BN-001", "Bolsa negra mediana", D("35.00"), D("17.50"), D("0.58"), D("0.65"), 60, True, True, "7 595288 000005"),
            ("Bolsas Negras- Blancas", "Bolsa Blanca Grande", "BN-002", "Bolsa blanca grande", D("40.00"), D("20.00"), D("0.67"), D("0.72"), 60, False, True, "7 595288 000006"),
            ("Cubiertos", "Tenedores de Mesa", "CU-001", "Tenedores de mesa (caja)", D("48.00"), D("24.00"), D("0.80"), D("0.90"), 60, True, True, "7 595288 000007"),
            ("Cubiertos", "Cucharas de Sopa", "CU-002", "Cucharas de sopa (caja)", D("48.00"), D("24.00"), D("0.80"), D("0.90"), 60, False, True, "7 595288 000008"),
            ("Bwol", "Servilletas BWOL", "BW-001", "Servilletas BWOL (caja)", D("55.00"), D("27.50"), D("0.92"), D("1.00"), 60, True, True, "7 595288 000009"),
            ("Bwol", "Servilletas BWOL Premium", "BW-002", "Servilletas BWOL premium", D("65.00"), D("32.50"), D("1.08"), D("1.20"), 60, False, True, "7 595288 000010"),
            ("platos", "Platos Desechables 9", "PL-001", "Platos desechables 9 pulgadas", D("42.00"), D("21.00"), D("0.70"), D("0.80"), 60, True, True, "7 595288 000011"),
            ("platos", "Platos Desechables 10", "PL-002", "Platos desechables 10 pulgadas", D("45.00"), D("22.50"), D("0.75"), D("0.85"), 60, False, True, "7 595288 000012"),
            ("vasos", "Vasos Plásticos 12oz", "VA-001", "Vasos plásticos 12oz (caja)", D("32.00"), D("16.00"), D("0.53"), D("0.60"), 100, True, True, "7 595288 000013"),
            ("vasos", "Vasos Plásticos 16oz", "VA-002", "Vasos plásticos 16oz (caja)", D("38.00"), D("19.00"), D("0.63"), D("0.70"), 100, False, True, "7 595288 000014"),
            ("Cartucho transparente", "Cartucho 500ml", "CT-001", "Cartucho transparente 500ml", D("28.00"), D("14.00"), D("0.47"), D("0.55"), 50, True, True, "7 595288 000015"),
            ("Cartucho transparente", "Cartucho 1000ml", "CT-002", "Cartucho transparente 1000ml", D("35.00"), D("17.50"), D("0.58"), D("0.65"), 50, False, True, "7 595288 000016"),
        ]

        for (
            cat_nombre,
            nombre,
            sku,
            descripcion,
            precio_caja,
            precio_media_caja,
            precio_unidad,
            precio_consumidor,
            unidades,
            permite_media_caja,
            itbms,
            codigo_barras,
        ) in productos_datos:
            producto, created = Producto.objects.update_or_create(
                sku=sku,
                defaults={
                    "categoria": categorias[cat_nombre],
                    "nombre": nombre,
                    "descripcion_corta": descripcion,
                    "precio_caja": precio_caja,
                    "precio_media_caja": precio_media_caja,
                    "precio_unidad": precio_unidad,
                    "precio_consumidor": precio_consumidor,
                    "unidades_por_caja": unidades,
                    "permite_media_caja": permite_media_caja,
                    "aplica_itbms": itbms,
                    "estado_activo": True,
                    "codigo_barras": codigo_barras,
                },
            )
            if created:
                self.stdout.write(f"Producto creado: {sku} - {nombre}")
            else:
                self.stdout.write(f"Producto actualizado: {sku} - {nombre}")

        # Crear clientes B2B (si no existen)
        clientes_datos = [
            (
                "SUPERMERCADO EL PROGRESO S.A.",
                "1-2345678-90-123",
                "compras@elprogreso.example",
                "+507 200-1234",
                "Avenida Balboa, Ciudad de Panamá",
            ),
            (
                "DISTRIBUIDORA DEL ISTMO S.A.",
                "1-9876543-21-000",
                "pagos@istmo.example",
                "+507 300-5566",
                "Vía España, Panamá Viejo",
            ),
            (
                "TIENDAS DON PEPE",
                "8-102-456",
                "pedidos@donpepe.example",
                "+507 611-2233",
                "Calle 44, Apartado 3B, Bella Vista",
            ),
        ]

        for nombre, ruc, email, telefono, direccion in clientes_datos:
            cliente, created = ClienteB2B.objects.get_or_create(
                ruc=ruc,
                defaults={
                    "nombre_empresa": nombre,
                    "email_contacto": email,
                    "telefono": telefono,
                    "direccion": direccion,
                    "activo": True,
                },
            )
            if created:
                self.stdout.write(f"Cliente B2B creado: {nombre}")
            else:
                self.stdout.write(f"Cliente B2B ya existe: {nombre}")

        self.stdout.write(
            self.style.SUCCESS(
                f"Datos del catálogo listos:\n"
                f"  {Categoria.objects.count()} categorías\n"
                f"  {Producto.objects.count()} productos\n"
                f"  {ClienteB2B.objects.count()} clientes B2B"
            )
        )
