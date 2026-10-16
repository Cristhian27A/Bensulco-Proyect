"""Crea un pedido de ejemplo para probar la conversión a factura.

    python manage.py seed_pedido
"""

from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from catalogo.models import ClienteB2B, LineaPedidoB2B, PedidoB2B, Producto

D = Decimal


class Command(BaseCommand):
    help = "Crea un pedido de ejemplo para probar la conversión a factura."

    def handle(self, *args, **options):
        # Obtener un cliente existente o crear uno
        cliente = ClienteB2B.objects.filter(activo=True).first()
        if not cliente:
            cliente = ClienteB2B.objects.create(
                nombre_empresa="Cliente de Prueba S.A.",
                ruc="1-1112222-33-444",
                email_contacto="prueba@test.com",
                telefono="+507 5555-5555",
                direccion="Dirección de prueba",
                activo=True,
            )
            self.stdout.write("Cliente de prueba creado.")

        # Obtener productos activos
        productos = Producto.objects.filter(estado_activo=True)[:3]

        if not productos:
            self.stdout.write(
                self.style.ERROR("No hay productos activos. Ejecute seed_catalogo primero.")
            )
            return

        # Crear el pedido
        with transaction.atomic():
            pedido = PedidoB2B.objects.create(
                cliente=cliente,
                estado=PedidoB2B.ESTADO_PENDIENTE,
                total_estimado=D("0"),
                notas="Pedido de prueba para conversión a factura.",
            )

            total = D("0")
            for orden, producto in enumerate(productos, start=1):
                cantidad_cajas = D("1")
                cantidad_unidades = D("0")
                subtotal = cantidad_cajas * producto.precio_caja

                LineaPedidoB2B.objects.create(
                    pedido=pedido,
                    producto=producto,
                    cantidad_cajas=cantidad_cajas,
                    cantidad_unidades=cantidad_unidades,
                    subtotal=subtotal,
                    orden=orden,
                )

                total += subtotal

            pedido.total_estimado = total
            pedido.save()

        self.stdout.write(
            self.style.SUCCESS(
                f"Pedido de prueba creado:\n"
                f"  Número: PED-{pedido.pk:04d}\n"
                f"  Cliente: {cliente.nombre_empresa}\n"
                f"  Estado: {pedido.get_estado_display()}\n"
                f"  Total: ${total:.2f}\n"
                f"  Productos: {len(productos)}\n\n"
                f"Ahora puede acceder a /pedidos/ para convertirlo a factura."
            )
        )
