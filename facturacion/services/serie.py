"""Generación del número de serie y del código de verificación.

Formato de serie: FAC-AAAA-0001, consecutivo por año y único.

El consecutivo se reserva dentro de ``transaction.atomic()`` con
``select_for_update()`` sobre la fila del contador del año, de modo que dos
peticiones simultáneas nunca puedan obtener el mismo número.
"""

import base64
import hashlib
import hmac
from datetime import date

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from facturacion.models import (
    ContadorOrdenCompra,
    ContadorSerie,
    COBRAR_POR_UNIDAD,
    Factura,
    LineaFactura,
)
from facturacion.services.totales import (
    CERO,
    COBRAR_POR_CAJA,
    calcular_linea,
    calcular_totales,
)

PREFIJO_SERIE = "FAC"
PREFIJO_ORDEN = "OC"
LARGO_CODIGO = 12

# Alfabeto base32 estándar (los 32 caracteres que usa la codificación base32).
BASE32 = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"

# Alfabeto de salida, sin caracteres que se confundan al leerlos en un PDF:
# no tiene 0, 1, 8, 9, I ni O.
ALFABETO = "23456789ABCDEFGHJKLMNPQRSTUVWXYZ"


def _letras_base32(datos: bytes, largo: int) -> str:
    """Convierte bytes a una cadena mayuscula sin caracteres ambiguos."""
    digitos = base64.b32encode(datos).decode("ascii").rstrip("=")
    salida = "".join(ALFABETO[BASE32.index(c)] for c in digitos)
    while len(salida) < largo:
        salida += "0"
    return salida[:largo]


def generar_codigo_verificacion(serie: str, total, fecha: date) -> str:
    """Código de 12 caracteres: HMAC-SHA256 con la SECRET_KEY.

    Se calcula sobre el contenido de la factura (serie, total y fecha),
    así que cualquier cambio altera el código.
    """
    secreto = str(settings.SECRET_KEY).encode("utf-8")
    mensaje = f"{serie}|{total:.2f}|{fecha.isoformat()}".encode("utf-8")
    resumen = hmac.new(secreto, mensaje, hashlib.sha256).digest()
    return _letras_base32(resumen, LARGO_CODIGO)


def siguiente_numero_serie(fecha: date) -> str:
    """Devuelve el siguiente número de serie del año de ``fecha``.

    Debe llamarse dentro de un ``transaction.atomic()``. La fila del
    contador queda bloqueada con ``select_for_update()`` hasta el final de la
    transacción, de modo que no se repiten números.
    """
    anio = fecha.year
    contador, _creado = ContadorSerie.objects.select_for_update().get_or_create(
        anio=anio, defaults={"ultimo_numero": 0}
    )
    siguiente = contador.ultimo_numero + 1
    contador.ultimo_numero = siguiente
    contador.save(update_fields=["ultimo_numero"])
    return f"{PREFIJO_SERIE}-{anio}-{siguiente:04d}"


def siguiente_numero_orden(fecha: date) -> str:
    """Devuelve la siguiente orden de compra OC-AAAA-0001 del año.

    Su propio contador, aparte del de la serie. Debe llamarse dentro de un
    ``transaction.atomic()`` con la fila bloqueada, igual que la serie: la
    factura anulada no libera su número de orden de compra.
    """
    anio = fecha.year
    contador, _creado = ContadorOrdenCompra.objects.select_for_update().get_or_create(
        anio=anio, defaults={"ultimo_numero": 0}
    )
    siguiente = contador.ultimo_numero + 1
    contador.ultimo_numero = siguiente
    contador.save(update_fields=["ultimo_numero"])
    return f"{PREFIJO_ORDEN}-{anio}-{siguiente:04d}"


def verificar_codigo(serie: str, codigo: str, total, fecha: date) -> bool:
    """Compara el código recibido con el calculado de la factura."""
    if not serie or not codigo:
        return False
    esperado = generar_codigo_verificacion(serie, total, fecha)
    return hmac.compare_digest(esperado, codigo.strip().upper())


def _texto(linea, campo: str) -> str:
    """Lee un campo de texto de una línea, sea diccionario u objeto."""
    if isinstance(linea, dict):
        return str(linea.get(campo) or "")
    return str(getattr(linea, campo, "") or "")


@transaction.atomic
def crear_factura(datos_factura: dict, lineas: list) -> Factura:
    """Crea la factura con su número de serie, código de verificación y totales.

    ``datos_factura``: diccionario con los campos del modelo, incluida la fecha.
    ``lineas``: lista de diccionarios con ``descripcion``, ``codigo_barras``,
    ``categoria``, ``cantidad``, ``precio_unitario`` y ``gravada``.
    """
    fecha = datos_factura["fecha"]
    if isinstance(fecha, str):
        fecha = timezone.datetime.strptime(fecha, "%Y-%m-%d").date()

    # Los totales se calculan antes de la serie porque el código de
    # verificación depende del monto final.
    lineas_preparadas = []
    calculadas = []
    for linea in lineas:
        datos = {
            "descripcion": _texto(linea, "descripcion"),
            "codigo_barras": _texto(linea, "codigo_barras"),
            "categoria": _texto(linea, "categoria"),
            "cantidad": _numero(linea, "cantidad"),
            "precio_unitario": _numero(linea, "precio_unitario"),
            "precio_unidad": _numero(linea, "precio_unidad") if linea.get("precio_unidad") else None,
            # El descuento sigue existiendo en el modelo, siempre en 0.
            "descuento_pct": CERO,
            "gravada": _numero(linea, "gravada"),
            "unidades_por_caja": _unidades_de_caja(linea),
            "cobrar_por": _cobrar_por(linea),
        }
        lineas_preparadas.append(datos)
        calculadas.append(
            calcular_linea(
                cantidad=datos["cantidad"],
                precio_unitario=datos["precio_unitario"],
                descuento_pct=datos["descuento_pct"],
                gravada=datos["gravada"],
                unidades_por_caja=datos["unidades_por_caja"],
                cobrar_por=datos["cobrar_por"],
                precio_unidad=datos["precio_unidad"],
            )
        )

    totales = calcular_totales(
        calculadas,
        itbms_activo=datos_factura.get("itbms_activo", True),
    )

    numero_serie = siguiente_numero_serie(fecha)
    # La orden de compra se puede escribir a mano; si viene vacia, se asigna
    # una automatica con su propio consecutivo por ano.
    orden_compra = (datos_factura.get("orden_compra") or "").strip()
    if not orden_compra:
        orden_compra = siguiente_numero_orden(fecha)

    factura = Factura(
        numero_serie=numero_serie,
        codigo_verificacion="",
        fecha=fecha,
        cliente_nombre=datos_factura["cliente_nombre"],
        cliente_ruc=datos_factura.get("cliente_ruc", ""),
        mostrar_ruc=datos_factura.get("mostrar_ruc", True),
        cliente_direccion=datos_factura.get("cliente_direccion", ""),
        cliente_telefono=datos_factura.get("cliente_telefono", ""),
        cliente_correo=datos_factura.get("cliente_correo", ""),
        sucursal=datos_factura.get("sucursal", ""),
        orden_compra=orden_compra,
        vendedor=datos_factura.get("vendedor", ""),
        condicion_pago=datos_factura.get("condicion_pago", Factura.CONDICION_CONTADO),
        portes=CERO,
        notas=datos_factura.get("notas", "") or "",
        subtotal=totales.subtotal,
        descuento_total=totales.descuento_total,
        base_gravada=totales.base_gravada,
        base_exenta=totales.base_exenta,
        itbms=totales.itbms,
        total=totales.total,
    )
    factura.codigo_verificacion = generar_codigo_verificacion(
        numero_serie, factura.total, factura.fecha
    )
    factura.save()

    for indice, (datos, calculo) in enumerate(zip(lineas_preparadas, totales.lineas), start=1):
        LineaFactura.objects.create(
            factura=factura,
            orden=indice,
            descripcion=datos["descripcion"],
            codigo_barras=datos["codigo_barras"],
            categoria=datos["categoria"],
            cantidad=calculo.cantidad,
            precio_unitario=calculo.precio_unitario,
            precio_unidad=datos["precio_unidad"],
            descuento_pct=calculo.descuento_pct,
            gravada=calculo.gravada,
            unidades_por_caja=calculo.unidades_por_caja,
            cobrar_por=calculo.cobrar_por,
            monto=calculo.monto,
        )

    return factura


def _unidades_de_caja(linea) -> int:
    """Unidades por caja de una linea, minimo 1 y sin decimales."""
    valor = _texto(linea, "unidades_por_caja") or "1"
    try:
        unidades = int(float(valor))
    except (TypeError, ValueError):
        return 1
    return unidades if unidades >= 1 else 1


def _cobrar_por(linea) -> str:
    """Modo de cobro de una linea: por unidad o por caja."""
    valor = _texto(linea, "cobrar_por")
    if valor == COBRAR_POR_CAJA:
        return COBRAR_POR_CAJA
    return COBRAR_POR_UNIDAD


def _numero(linea, campo: str):
    """Lee un campo numérico o booleano de una línea."""
    if isinstance(linea, dict):
        valor = linea.get(campo)
    else:
        valor = getattr(linea, campo, None)
    if valor is None or valor == "":
        return CERO if campo != "gravada" else True
    return valor


def anular_factura(factura: Factura) -> Factura:
    """Marca la factura como anulada. Una factura emitida no se edita."""
    factura.estado = Factura.ESTADO_ANULADA
    factura.fecha_anulacion = timezone.now()
    factura.save(update_fields=["estado", "fecha_anulacion"])
    return factura
