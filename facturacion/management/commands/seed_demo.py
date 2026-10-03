"""Crea datos de ejemplo para probar la aplicacion.

    python manage.py seed_demo

Genera la configuracion del negocio, varias facturas de un año y una factura
anulada, y deja dos facturas para revisar el PDF: una de 12 productos que cabe
en una hoja y otra de 40 productos que ocupa varias.
"""

from datetime import date
from decimal import Decimal
import re

from django.core.management.base import BaseCommand
from django.db import transaction

from facturacion.models import (
    COBRAR_POR_CAJA,
    COBRAR_POR_UNIDAD,
    ConfiguracionNegocio,
    ContadorOrdenCompra,
    ContadorSerie,
    Factura,
)
from facturacion.services.serie import anular_factura, crear_factura

D = Decimal

CLIENTES = [
    {
        "cliente_nombre": "SUPERMERCADO EL PROGRESO S.A.",
        "cliente_ruc": "1-2345678-90-123",
        "cliente_direccion": "Avenida Balboa, Ciudad de Panamá",
        "cliente_telefono": "+507 200-1234",
        "cliente_correo": "compras@elprogreso.example",
        "sucursal": "Sucursal Centro",
    },
    {
        "cliente_nombre": "DISTRIBUIDORA DEL ISTMO S.A.",
        "cliente_ruc": "1-9876543-21-000",
        "cliente_direccion": "Vía España, Panamá Viejo",
        "cliente_telefono": "+507 300-5566",
        "cliente_correo": "pagos@istmo.example",
        "sucursal": "Sucursal Cerro Viento",
    },
    {
        "cliente_nombre": "María González",
        "cliente_ruc": "8-102-456",
        "cliente_direccion": "Calle 44, Apartado 3B, Bella Vista",
        "cliente_telefono": "+507 611-2233",
        "cliente_correo": "maria.gonzalez@example.com",
        "sucursal": "Sucursal Bella Vista",
    },
]

PRODUCTOS = [
    # Descripcion, categoria, precio
    ("Aceite vegetal 900 ml", "Abarrotes", "4.85"),
    ("Arroz precocido 5 lb", "Abarrotes", "6.20"),
    ("Azúcar refinada 2 kg", "Abarrotes", "3.40"),
    ("Leche entera 1 L", "Lácteos", "1.95"),
    ("Queso blanco 500 g", "Lácteos", "5.60"),
    ("Jamón cocido 250 g", "Carnes", "4.10"),
    ("Pan dulce", "Panadería", "0.60"),
    ("Galletas de soda", "Panadería", "1.25"),
    ("Jabón de ropa 3 L", "Limpieza", "5.90"),
    ("Cloro desinfectante 2 L", "Limpieza", "2.35"),
    ("Detergente en polvo 5 kg", "Limpieza", "9.75"),
    ("Papel higiénico 12 rollos", "Limpieza", "7.40"),
    ("Café molido 500 g", "Bebidas", "7.90"),
    ("Jugo de naranja 1 L", "Bebidas", "2.10"),
    ("Agua mineral 1.5 L", "Bebidas", "1.15"),
    ("Guantes de nitrilo 100", "Varios", "6.50"),
    ("Pilas AA 4", "Varios", "3.20"),
    ("Fósforos caja 12", "Varios", "1.05"),
    ("Bolsas plásticas medianas 100", "Limpieza", "30.00"),
    ("Papel aluminio 24 und", "Abarrotes", "12.00"),
]

# Productos que se venden por caja o por unidad con caja de N unidades:
#   clave -> (unidades_por_caja, cobrar_por)
EN_CAJA = {
    "Bolsas plásticas medianas 100": (100, COBRAR_POR_CAJA),
    "Papel aluminio 24 und": (24, COBRAR_POR_UNIDAD),
}

# Las doce primeras caben en una sola hoja de carta.
PRODUCTOS_DE_UNA_HOJA = PRODUCTOS[:12]

# Para la factura que se repite en varias paginas hace falta mas de una decena
# de productos, asi que se repite el catalogo hasta llegar a cuarenta.
CANTIDAD_DE_PRODUCTOS_MULTIPAGINA = 40


def productos_repetidos(cantidad):
    """Devuelve `cantidad` productos, repitiendo el catalogo si hace falta."""
    vueltas = -(-cantidad // len(PRODUCTOS))
    repetido = [
        (f"{descripcion} (parte {vuelta + 1})" if vuelta else descripcion,
         categoria, precio)
        for vuelta in range(vueltas)
        for descripcion, categoria, precio in PRODUCTOS
    ]
    return repetido[:cantidad]


def caja_de(descripcion) -> dict:
    """Datos de caja de un producto repetido, o vacío si no aplica."""
    base = re.sub(r" \(parte \d+\)$", "", descripcion)
    if base in EN_CAJA:
        unidades, cobrar_por = EN_CAJA[base]
        return {"unidades_por_caja": unidades, "cobrar_por": cobrar_por}
    return {}


def linea(descripcion, categoria, precio, cantidad, adicionales=None):
    """Una linea de producto. El monto es cantidad x precio (caja o unidad)."""
    datos = {
        "descripcion": descripcion,
        "codigo_barras": f"7501{abs(hash(descripcion)) % 10**8:08d}",
        "categoria": categoria,
        "cantidad": D(cantidad),
        "precio_unitario": D(precio),
        "gravada": True,
    }
    if adicionales:
        datos.update(adicionales)
    return datos


class Command(BaseCommand):
    help = "Carga datos de ejemplo: configuracion, facturas y una anulada."

    def add_arguments(self, parser):
        parser.add_argument(
            "--borrar",
            action="store_true",
            help="Borra las facturas de ejemplo antes de crearlas de nuevo.",
        )

    @transaction.atomic
    def handle(self, *args, **opciones):
        if opciones["borrar"]:
            borradas = Factura.objects.all().delete()
            self.stdout.write(f"Se borraron {borradas[0]} registros de factura.")
            # El consecutivo tambien vuelve a cero, para que el ejemplo
            # empiece otra vez en FAC-AAAA-0001 (y la OC en OC-AAAA-0001).
            ContadorSerie.objects.all().delete()
            ContadorOrdenCompra.objects.all().delete()

        configuracion = ConfiguracionNegocio.cargar()
        # Con --borrar se reinicia todo, incluida la configuracion, para que el
        # ejemplo siempre salga igual. Sin --borrar solo se rellenan los campos
        # de una configuracion que sigue siendo la de ejemplo.
        if opciones["borrar"] or configuracion.empresa_nombre.endswith("(EJEMPLO)"):
            configuracion.empresa_nombre = "COMERCIAL SANTA ANA S.A."
            configuracion.empresa_ruc = "1-2223333-44-55"
            configuracion.mostrar_ruc = True
            configuracion.empresa_direccion = (
                "Calle 50 entre la Avenida Central y Balboa, Ciudad de Panamá"
            )
            configuracion.empresa_telefono = "+507 264-5500"
            configuracion.empresa_correo = "facturacion@comercialsantana.example"
            configuracion.datos_bancarios = (
                "Banco Nacional de Panamá\n"
                "Cuenta: 010-999-888-77777\n"
                "A nombre de Comercial Santa Ana S.A."
            )
            configuracion.notas_predeterminadas = (
                "Conserve esta factura y preséntela para cualquier reclamo.\n"
                "Gracias por su compra."
            )
            configuracion.color_principal = "#3A0088"
            configuracion.color_barra_factura = "#5B3A9E"
            configuracion.color_tabla = "#3A0088"
            configuracion.save()
            self.stdout.write("Configuracion del negocio actualizada.")

        anio = date.today().year
        mes = date.today().month
        creadas = []

        # Tres facturas de meses distintos, para que el historial tenga de todo.
        for numero, (mes_factura, condicion, indice_cliente) in enumerate(
            [
                (max(1, mes - 2), Factura.CONDICION_CREDITO, 0),
                (max(1, mes - 1), Factura.CONDICION_CONTADO, 1),
                (mes, Factura.CONDICION_CREDITO, 2),
            ],
            start=1,
        ):
            fecha = date(anio, mes_factura, 5 * numero)
            cliente = CLIENTES[indice_cliente]
            productos = PRODUCTOS[numero * 2:numero * 2 + 6]
            factura = crear_factura(
                {
                    "fecha": fecha,
                    "condicion_pago": condicion,
                    "vendedor": "María Pérez" if numero % 2 else "Luis Batista",
                    "notas": "",
                    "itbms_activo": True,
                    **cliente,
                },
                [
                    linea(descripcion, categoria, precio,
                          cantidad=str((numero + i) % 3 + 1))
                    for i, (descripcion, categoria, precio) in enumerate(productos)
                ],
            )
            creadas.append(factura)

        # Una factura anulada, para ver la marca de agua del PDF.
        anulada = crear_factura(
            {
                "fecha": date(anio, mes, 3),
                "condicion_pago": Factura.CONDICION_CONTADO,
                "vendedor": "Luis Batista",
                "notas": "El cliente devolvió la mercancia.",
                "itbms_activo": True,
                **CLIENTES[1],
            },
            [
                linea("Aceite vegetal 900 ml", "Abarrotes", "4.85", "2"),
                linea("Leche entera 1 L", "Lácteos", "1.95", "6"),
            ],
        )
        anular_factura(anulada)
        creadas.append(anulada)

        # Factura de una sola hoja, con doce productos de descripcion corta.
        una_hoja = crear_factura(
            {
                "fecha": date(anio, mes, 20),
                "condicion_pago": Factura.CONDICION_CONTADO,
                "vendedor": "María Pérez",
                "notas": (
                    "Entrega a domicilio en menos de 24 horas.\n"
                    "Gracias por preferirnos."
                ),
                "itbms_activo": True,
                **CLIENTES[0],
            },
            [
                linea(descripcion, categoria, precio, cantidad=str(i % 4 + 1))
                for i, (descripcion, categoria, precio)
                in enumerate(PRODUCTOS_DE_UNA_HOJA)
            ],
        )
        creadas.append(una_hoja)

        # Factura de varias paginas, con cuarenta productos.
        varias_paginas = crear_factura(
            {
                "fecha": date(anio, mes, 22),
                "condicion_pago": Factura.CONDICION_CREDITO,
                "vendedor": "Luis Batista",
                "notas": (
                    "Pedido al por mayor. Entrega en el almacen del cliente.\n"
                    "Revisar el empaque antes de firmar la recepcion."
                ),
                "itbms_activo": True,
                **CLIENTES[1],
            },
            [
                linea(
                    descripcion, categoria, precio,
                    cantidad=str(i % 5 + 1),
                    adicionales=caja_de(descripcion),
                )
                for i, (descripcion, categoria, precio)
                in enumerate(productos_repetidos(CANTIDAD_DE_PRODUCTOS_MULTIPAGINA))
            ],
        )
        creadas.append(varias_paginas)

        for factura in creadas:
            marca = " (anulada)" if factura.anulada else ""
            self.stdout.write(
                f"  {factura.numero_serie}  {factura.cliente_nombre}"
                f"  {factura.total:,.2f}{marca}"
            )

        self.stdout.write(self.style.SUCCESS(
            f"Datos de ejemplo listos: {len(creadas)} facturas en el año {anio}."
        ))
        self.stdout.write(
            f"Factura de una hoja (12 productos): {una_hoja.numero_serie}"
        )
        self.stdout.write(
            f"Factura de varias hojas "
            f"({CANTIDAD_DE_PRODUCTOS_MULTIPAGINA} productos): "
            f"{varias_paginas.numero_serie}"
        )
