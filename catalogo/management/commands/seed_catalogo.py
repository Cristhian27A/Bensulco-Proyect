"""Crea datos de ejemplo para el catálogo de productos.

    python manage.py seed_catalogo

Genera categorías, productos y clientes B2B de ejemplo para probar
el sistema de pedidos.
"""

from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from catalogo.models import Categoria, ClienteB2B, Producto

D = Decimal


class Command(BaseCommand):
    help = "Carga datos de ejemplo para el catálogo de productos y clientes B2B."

    def add_arguments(self, parser):
        parser.add_argument(
            "--borrar",
            action="store_true",
            help="Borra los datos existentes antes de crear los nuevos.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options["borrar"]:
            Producto.objects.all().delete()
            Categoria.objects.all().delete()
            ClienteB2B.objects.all().delete()
            self.stdout.write("Datos existentes borrados.")

        # Crear categorías
        categorias_datos = [
            "Abarrotes",
            "Lácteos",
            "Carnes",
            "Panadería",
            "Bebidas",
            "Limpieza",
            "Varios",
        ]

        categorias = {}
        for nombre in categorias_datos:
            categoria, _ = Categoria.objects.get_or_create(nombre=nombre)
            categorias[nombre] = categoria
            self.stdout.write(f"Categoría creada: {nombre}")

        # Crear productos
        productos_datos = [
            # (categoria, nombre, sku, descripcion, precio_caja, precio_unidad, unidades_por_caja, aplica_itbms)
            ("Abarrotes", "Aceite vegetal 900 ml", "ACE-001", "Aceite vegetal de 900 ml", D("4.85"), D("0.16"), 30, True),
            ("Abarrotes", "Arroz precocido 5 lb", "ARR-001", "Arroz precocido de 5 libras", D("6.20"), D("1.24"), 5, True),
            ("Abarrotes", "Azúcar refinada 2 kg", "AZU-001", "Azúcar refinada de 2 kg", D("3.40"), D("1.70"), 2, True),
            ("Lácteos", "Leche entera 1 L", "LEC-001", "Leche entera de 1 litro", D("1.95"), D("1.95"), 1, True),
            ("Lácteos", "Queso blanco 500 g", "QUE-001", "Queso blanco de 500 gramos", D("5.60"), D("0.56"), 10, True),
            ("Carnes", "Jamón cocido 250 g", "JAM-001", "Jamón cocido de 250 gramos", D("4.10"), D("0.82"), 5, True),
            ("Panadería", "Pan dulce", "PAN-001", "Pan dulce por unidad", D("0.60"), D("0.60"), 1, True),
            ("Panadería", "Galletas de soda", "GAL-001", "Galletas de soda paquete", D("1.25"), D("0.25"), 5, True),
            ("Limpieza", "Jabón de ropa 3 L", "JAB-001", "Jabón de ropa de 3 litros", D("5.90"), D("1.97"), 3, True),
            ("Limpieza", "Cloro desinfectante 2 L", "CLO-001", "Cloro desinfectante de 2 litros", D("2.35"), D("1.18"), 2, True),
            ("Limpieza", "Detergente en polvo 5 kg", "DET-001", "Detergente en polvo de 5 kg", D("9.75"), D("1.95"), 5, True),
            ("Limpieza", "Papel higiénico 12 rollos", "PAH-001", "Papel higiénico 12 rollos", D("7.40"), D("0.62"), 12, True),
            ("Bebidas", "Café molido 500 g", "CAF-001", "Café molido de 500 gramos", D("7.90"), D("0.79"), 10, True),
            ("Bebidas", "Jugo de naranja 1 L", "JUG-001", "Jugo de naranja de 1 litro", D("2.10"), D("2.10"), 1, True),
            ("Bebidas", "Agua mineral 1.5 L", "AGU-001", "Agua mineral de 1.5 litros", D("1.15"), D("0.58"), 2, True),
            ("Varios", "Guantes de nitrilo 100", "GUI-001", "Guantes de nitrilo (caja de 100)", D("6.50"), D("0.065"), 100, True),
            ("Varios", "Pilas AA 4", "PIL-001", "Pilas AA (paquete de 4)", D("3.20"), D("0.80"), 4, True),
            ("Varios", "Fósforos caja 12", "FOS-001", "Caja de fósforos de 12", D("1.05"), D("0.09"), 12, True),
        ]

        for (
            cat_nombre,
            nombre,
            sku,
            descripcion,
            precio_caja,
            precio_unidad,
            unidades,
            itbms,
        ) in productos_datos:
            Producto.objects.get_or_create(
                sku=sku,
                defaults={
                    "categoria": categorias[cat_nombre],
                    "nombre": nombre,
                    "descripcion_corta": descripcion,
                    "precio_caja": precio_caja,
                    "precio_unidad": precio_unidad,
                    "unidades_por_caja": unidades,
                    "aplica_itbms": itbms,
                    "estado_activo": True,
                },
            )
            self.stdout.write(f"Producto creado: {sku} - {nombre}")

        # Crear clientes B2B
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
            ClienteB2B.objects.get_or_create(
                ruc=ruc,
                defaults={
                    "nombre_empresa": nombre,
                    "email_contacto": email,
                    "telefono": telefono,
                    "direccion": direccion,
                    "activo": True,
                },
            )
            self.stdout.write(f"Cliente B2B creado: {nombre}")

        self.stdout.write(
            self.style.SUCCESS(
                f"Datos de ejemplo del catálogo listos:\n"
                f"  {Categoria.objects.count()} categorías\n"
                f"  {Producto.objects.count()} productos\n"
                f"  {ClienteB2B.objects.count()} clientes B2B"
            )
        )
