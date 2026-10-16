"""Calculo de montos de una factura.

Este modulo es la unica fuente de la verdad. El JavaScript del formulario
copia exactamente estas formulas para mostrar los totales en vivo mientras
el usuario escribe, y las pruebas verifican que ambos coincidan.

Reglas:

* Todo se trabaja con ``Decimal``, nunca con ``float``.
* El monto de una linea se calcula en una sola operacion y se redondea una
  sola vez al final con ``ROUND_HALF_UP`` a dos decimales.
* El descuento que se informa en el cuadro de totales es la diferencia entre
  la suma de (cantidad x precio) y la suma de los montos ya redondeados.
  Asi ``subtotal - descuento = base`` siempre cuadra al centavo.
* Cuando no hay descuentos (como siempre sale la factura), el subtotal es
  exactamente la suma de los montos de las lineas, para que
  ``total = subtotal + ITBMS`` cuadre al centavo.
"""

from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP

DOS_DECIMALES = Decimal("0.01")
CERO = Decimal("0.00")
CIENTO = Decimal("100")
PORCENTAJE_ITBMS = Decimal("0.07")

COBRAR_POR_UNIDAD = "unidad"
COBRAR_POR_CAJA = "caja"


def _unidades_por_caja(valor) -> int:
    """El numero entero de unidades que trae la caja (minimo 1)."""
    try:
        unidades = int(valor or 1)
    except (TypeError, ValueError):
        unidades = 1
    return unidades if unidades >= 1 else 1


def a_decimal(valor) -> Decimal:
    """Convierte a Decimal sin arrastrar errores de coma flotante."""
    if isinstance(valor, Decimal):
        return valor
    if valor is None or valor == "":
        return CERO
    return Decimal(str(valor))


def redondear(valor) -> Decimal:
    """Redondea a dos decimales usando ROUND_HALF_UP (0.005 sube a 0.01)."""
    return a_decimal(valor).quantize(DOS_DECIMALES, rounding=ROUND_HALF_UP)


def precio_por_unidad(precio_caja, unidades_por_caja=1) -> Decimal:
    """Precio de una unidad suelta: el de la caja dividido por cuantas trae.

    No se redondea aqui: el PDF lo muestra redondeado a lo mas con 4
    decimales y el monto de la linea se redondea una sola vez al final.
    """
    return a_decimal(precio_caja) / _unidades_por_caja(unidades_por_caja)


def precio_efectivo(precio_caja, unidades_por_caja=1,
                    cobrar_por=COBRAR_POR_UNIDAD, precio_unidad=None) -> Decimal:
    """Precio por el que se multiplica la cantidad de la linea.

    "caja" usa el precio de la caja completo; "unidad" usa el precio_unitario
    directamente (para tiendas pequeñas que venden por unidad).
    """
    if cobrar_por == COBRAR_POR_CAJA:
        return a_decimal(precio_caja)
    # Para unidad: usa precio_unitario directamente (no divide precio_caja)
    if precio_unidad is not None and precio_unidad > CERO:
        return a_decimal(precio_unidad)
    # Fallback: usa precio_caja como precio_unitario si no se especifica
    return a_decimal(precio_caja)


def formato_precio(valor, decimales_max=4) -> str:
    """Formatea un precio hasta ``decimales_max``, sin ceros de mas.

        precio_por_unidad("30",  1) -> "30.00"
        precio_por_unidad("30", 24) -> "1.25"
        precio_por_unidad("10",  3) -> "3.3333"

    Solo se llega a 4 decimales cuando el precio de la unidad no es exacto.
    """
    texto = f"{a_decimal(valor):.{decimales_max}f}".rstrip("0").rstrip(".")
    if "." not in texto:
        return texto + ".00"
    entero, decimal = texto.split(".")
    if len(decimal) == 1:
        decimal += "0"
    return f"{entero}.{decimal}"


def monto_linea(cantidad, precio_caja, descuento_pct=CERO,
                unidades_por_caja=1, cobrar_por=COBRAR_POR_UNIDAD,
                precio_unidad=None) -> Decimal:
    """Monto de una linea, redondeado una sola vez.

    Si ``cobrar_por`` es "caja": cantidad_cajas * precio_caja.
    Si ``cobrar_por`` es "unidad": cantidad_unidades * precio_unitario.
    """
    cantidad = a_decimal(cantidad)
    precio = a_decimal(precio_caja)
    descuento = a_decimal(descuento_pct)

    if cantidad <= CERO or precio < CERO:
        return CERO

    # Determinar el precio efectivo según el modo de cobro
    if cobrar_por == COBRAR_POR_CAJA:
        bruto = cantidad * precio
    else:
        # Para unidad: usa precio_unitario directo (precio_caja en este caso es el precio por unidad)
        precio_usar = precio_unidad if (precio_unidad is not None and precio_unidad > CERO) else precio
        bruto = cantidad * precio_usar

    if descuento > CERO:
        if descuento >= CIENTO:
            return CERO
        factor = (CIENTO - descuento) / CIENTO
        return redondear(bruto * factor)

    return redondear(bruto)


@dataclass
class LineaCalculo:
    """Una linea ya calculada, tal como la usa el servidor y el PDF."""

    cantidad: Decimal
    precio_unitario: Decimal
    descuento_pct: Decimal
    gravada: bool
    monto: Decimal
    unidades_por_caja: int = 1
    cobrar_por: str = COBRAR_POR_UNIDAD
    precio_unidad: Decimal = None

    @property
    def precio_para_mostrar(self) -> Decimal:
        """El precio que se ve en el PDF: la caja o la unidad."""
        return precio_efectivo(
            self.precio_unitario, self.unidades_por_caja, self.cobrar_por, self.precio_unidad
        )

    @property
    def bruto(self) -> Decimal:
        """Cantidad x precio (de la caja o de la unidad) sin descuento."""
        return self.cantidad * self.precio_para_mostrar


@dataclass
class Totales:
    """Resultado del calculo completo de una factura."""

    lineas: list = field(default_factory=list)
    subtotal: Decimal = CERO
    descuento_total: Decimal = CERO
    base_gravada: Decimal = CERO
    base_exenta: Decimal = CERO
    itbms: Decimal = CERO
    portes: Decimal = CERO
    total: Decimal = CERO

    @property
    def base(self) -> Decimal:
        return self.base_gravada + self.base_exenta

    def como_texto(self) -> dict:
        """Valores ya formateados para la plantilla y el PDF."""
        return {
            "subtotal": f"{self.subtotal:,.2f}",
            "descuento_total": f"{self.descuento_total:,.2f}",
            "base_gravada": f"{self.base_gravada:,.2f}",
            "base_exenta": f"{self.base_exenta:,.2f}",
            "itbms": f"{self.itbms:,.2f}",
            "portes": f"{self.portes:,.2f}",
            "total": f"{self.total:,.2f}",
        }


def calcular_linea(cantidad, precio_unitario, descuento_pct=CERO, gravada=True,
                   unidades_por_caja=1, cobrar_por=COBRAR_POR_UNIDAD,
                   precio_unidad=None) -> LineaCalculo:
    """Prepara una linea con su monto ya redondeado.

    ``precio_unitario`` es el precio de la CAJA completa. Si ``cobrar_por``
    es "unidad" y se proporciona ``precio_unidad``, se usa directamente.
    Si no, divide el precio de la caja entre las unidades de la caja.
    """
    cantidad = a_decimal(cantidad)
    precio = a_decimal(precio_unitario)
    descuento = a_decimal(descuento_pct)
    unidades = _unidades_por_caja(unidades_por_caja)
    if cobrar_por not in (COBRAR_POR_UNIDAD, COBRAR_POR_CAJA):
        cobrar_por = COBRAR_POR_UNIDAD
    if cantidad < CERO:
        cantidad = CERO
    if descuento < CERO:
        descuento = CERO
    if descuento > CERO and descuento > CIENTO:
        descuento = CIENTO
    return LineaCalculo(
        cantidad=cantidad,
        precio_unitario=precio,
        descuento_pct=redondear(descuento),
        gravada=bool(gravada),
        unidades_por_caja=unidades,
        cobrar_por=cobrar_por,
        monto=monto_linea(cantidad, precio, descuento, unidades, cobrar_por, precio_unidad),
    )


def calcular_totales(lineas, portes=CERO, itbms_activo=True) -> Totales:
    """Calcula todos los totales de la factura.

    ``lineas`` es una lista de diccionarios o de objetos con las claves
    ``cantidad``, ``precio_unitario``, ``descuento_pct`` y ``gravada``
    (o atributos con esos nombres, por ejemplo un ``LineaFactura``).
    """
    calculadas = []
    suma_bruta = Decimal("0")
    base_gravada = Decimal("0")
    base_exenta = Decimal("0")
    hay_descuentos = False

    for item in lineas:
        if isinstance(item, LineaCalculo):
            linea = item
        else:
            datos = _leer_item(item)
            linea = calcular_linea(
                cantidad=datos["cantidad"],
                precio_unitario=datos["precio_unitario"],
                descuento_pct=datos["descuento_pct"],
                gravada=datos["gravada"],
                unidades_por_caja=datos["unidades_por_caja"],
                cobrar_por=datos["cobrar_por"],
                precio_unidad=datos["precio_unidad"],
            )
        calculadas.append(linea)
        suma_bruta += linea.bruto
        if linea.descuento_pct > CERO:
            hay_descuentos = True
        if linea.gravada and itbms_activo:
            base_gravada += linea.monto
        else:
            base_exenta += linea.monto

    base_gravada = redondear(base_gravada)
    base_exenta = redondear(base_exenta)
    base = base_gravada + base_exenta

    if hay_descuentos:
        # Con descuentos, el subtotal se redondea una sola vez sobre la suma
        # de los brutos y el descuento informado es la diferencia real, para
        # que subtotal - descuento = base cuadre al centavo.
        subtotal = redondear(suma_bruta)
        descuento_total = redondear(subtotal - base)
        if descuento_total < CERO:
            descuento_total = CERO
    else:
        # Sin descuentos (como se usa en la factura) el subtotal es
        # exactamente la suma de los montos de las lineas: asi el total
        # cuadra siempre a subtotal + ITBMS.
        subtotal = base
        descuento_total = CERO

    itbms = redondear(base_gravada * PORCENTAJE_ITBMS) if itbms_activo else CERO
    portes = redondear(a_decimal(portes))
    if portes < CERO:
        portes = CERO

    total = redondear(base_gravada + base_exenta + itbms + portes)

    return Totales(
        lineas=calculadas,
        subtotal=subtotal,
        descuento_total=descuento_total,
        base_gravada=base_gravada,
        base_exenta=base_exenta,
        itbms=itbms,
        portes=portes,
        total=total,
    )


def _leer_item(item) -> dict:
    """Acepta diccionarios, objetos Django o namedtuples."""

    def obtener(nombre, defecto):
        if isinstance(item, dict):
            return item.get(nombre, defecto)
        return getattr(item, nombre, defecto)

    return {
        "cantidad": obtener("cantidad", CERO),
        "precio_unitario": obtener("precio_unitario", CERO),
        "precio_unidad": obtener("precio_unidad", None),
        "descuento_pct": obtener("descuento_pct", CERO),
        "gravada": obtener("gravada", True),
        "unidades_por_caja": obtener("unidades_por_caja", 1),
        "cobrar_por": obtener("cobrar_por", COBRAR_POR_UNIDAD),
    }
