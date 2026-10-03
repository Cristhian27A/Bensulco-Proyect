"""Modelos de la facturacion.

Solo hay cuatro tablas: la configuracion del negocio (una sola fila),
el contador de series por anio, las facturas y sus lineas de detalle.
No hay tabla de clientes ni de productos: la app es un historial.
"""

from decimal import Decimal

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from facturacion.services.totales import formato_precio, precio_efectivo

CERO = Decimal("0.00")
CIENTO = Decimal("100")

COBRAR_POR_UNIDAD = "unidad"
COBRAR_POR_CAJA = "caja"
COBRAR_POR_OPCIONES = [
    (COBRAR_POR_UNIDAD, "Unidad"),
    (COBRAR_POR_CAJA, "Caja"),
]


class ConfiguracionNegocio(models.Model):
    """Una unica fila con los datos que alimentan el encabezado del PDF."""

    empresa_nombre = models.CharField("Nombre de la empresa", max_length=150)
    empresa_ruc = models.CharField("RUC / DV", max_length=40, blank=True)
    mostrar_ruc = models.BooleanField(
        "Mostrar RUC/DV en el encabezado y en el pie", default=True
    )
    empresa_direccion = models.TextField("Direccion", blank=True)
    empresa_correo = models.EmailField("Correo", blank=True)
    empresa_telefono = models.CharField("Telefono", max_length=60, blank=True)
    logo = models.ImageField("Logo", upload_to="logos/", blank=True, null=True)
    color_principal = models.CharField(
        "Color principal",
        max_length=7,
        default="#3A0088",
        help_text="En hexadecimal, por ejemplo #3A0088",
    )
    color_barra_factura = models.CharField(
        "Color de la barra ORDEN DE COMPRA",
        max_length=7,
        default="#5B3A9E",
        help_text="Franja del titulo de la factura en el PDF.",
    )
    color_tabla = models.CharField(
        "Color de la tabla y los totales",
        max_length=7,
        default="#3A0088",
        help_text="Encabezado de la tabla y banda del gran total.",
    )
    datos_bancarios = models.TextField("Datos bancarios", blank=True)
    # Nota unica: sustituye a los antiguos "Tenga en cuenta" y "notas extra".
    notas_predeterminadas = models.TextField(
        "Texto de notas por defecto",
        blank=True,
        help_text="Se precarga en cada factura nueva y se puede editar o borrar.",
    )
    actualizado = models.DateTimeField("Actualizado", auto_now=True)

    class Meta:
        verbose_name = "Configuracion del negocio"
        verbose_name_plural = "Configuracion del negocio"

    def __str__(self):
        return self.empresa_nombre

    def save(self, *args, **kwargs):
        """Fuerza que siempre exista una sola fila."""
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """No se puede borrar la configuracion."""
        return

    @classmethod
    def cargar(cls):
        """Devuelve la fila unica, creandola con datos de ejemplo si hace falta."""
        obj, _ = cls.objects.get_or_create(
            pk=1,
            defaults={
                "empresa_nombre": "MI EMPRESA S.A. (EJEMPLO)",
                "empresa_ruc": "1-2345678-90-123 DV:45 (EJEMPLO)",
                "mostrar_ruc": True,
                "empresa_direccion": "Calle Falsa 123, Ciudad de Panamá (EJEMPLO)",
                "empresa_correo": "facturacion@miempresa.example (EJEMPLO)",
                "empresa_telefono": "+507 0000-0000 (EJEMPLO)",
                "color_principal": "#3A0088",
                "color_barra_factura": "#5B3A9E",
                "color_tabla": "#3A0088",
                "datos_bancarios": "Banco de Ejemplo\nCuenta: 000-000000000000",
                "notas_predeterminadas": (
                    "Este es un texto de ejemplo. Edite la Configuracion del "
                    "negocio para escribir sus propias notas."
                ),
            },
        )
        return obj


class ContadorSerie(models.Model):
    """Consecutivo por anio para el numero de serie FAC-AAAA-0001."""

    anio = models.PositiveIntegerField("Anio", unique=True)
    ultimo_numero = models.PositiveIntegerField("Ultimo numero", default=0)

    class Meta:
        verbose_name = "Contador de serie"
        verbose_name_plural = "Contadores de serie"
        ordering = ["-anio"]

    def __str__(self):
        return f"{self.anio}: {self.ultimo_numero}"


class ContadorOrdenCompra(models.Model):
    """Consecutivo por anio para la orden de compra OC-AAAA-0001.

    Va aparte del contador de la serie: aunque la factura esté anulada, su
    numero de orden de compra no se vuelve a usar.
    """

    anio = models.PositiveIntegerField("Anio", unique=True)
    ultimo_numero = models.PositiveIntegerField("Ultimo numero", default=0)

    class Meta:
        verbose_name = "Contador de orden de compra"
        verbose_name_plural = "Contadores de orden de compra"
        ordering = ["-anio"]

    def __str__(self):
        return f"{self.anio}: {self.ultimo_numero}"


class Factura(models.Model):
    """Una factura emitida. Nunca se edita: se anula o se duplica."""

    ESTADO_EMITIDA = "emitida"
    ESTADO_ANULADA = "anulada"
    ESTADOS = [
        (ESTADO_EMITIDA, "Emitida"),
        (ESTADO_ANULADA, "Anulada"),
    ]

    CONDICION_CONTADO = "contado"
    CONDICION_CREDITO = "credito"
    CONDICIONES_PAGO = [
        (CONDICION_CONTADO, "Contado"),
        (CONDICION_CREDITO, "Credito"),
    ]

    numero_serie = models.CharField("Numero de serie", max_length=20, unique=True)
    codigo_verificacion = models.CharField(
        "Codigo de verificacion", max_length=12
    )
    fecha = models.DateField("Fecha")

    cliente_nombre = models.CharField("Cliente", max_length=200)
    cliente_ruc = models.CharField("RUC del cliente", max_length=40, blank=True)
    mostrar_ruc = models.BooleanField("Mostrar RUC/DV en la factura", default=True)
    cliente_direccion = models.CharField("Direccion del cliente", max_length=250, blank=True)
    cliente_telefono = models.CharField("Telefono del cliente", max_length=60, blank=True)
    cliente_correo = models.EmailField("Correo del cliente", blank=True)
    sucursal = models.CharField("Comprar desde", max_length=150, blank=True)
    vendedor = models.CharField("Realizado por", max_length=150, blank=True)

    # La orden de compra se puede escribir a mano; si queda vacia, al guardar
    # se asigna una automatica (OC-AAAA-0001).
    orden_compra = models.CharField("N.o de orden de compra", max_length=60, blank=True)

    condicion_pago = models.CharField(
        "Condicion de pago", max_length=20, choices=CONDICIONES_PAGO,
        default=CONDICION_CONTADO,
    )

    # Portes sigue en el modelo (siempre 0) por si se reactiva.
    portes = models.DecimalField(
        "Portes", max_digits=14, decimal_places=2, default=CERO
    )
    # Nota unica de la factura. Reemplaza a "observaciones" y "notas_extra",
    # que se conservan vacias y ya no se usan.
    notas = models.TextField("Notas", blank=True)

    subtotal = models.DecimalField(max_digits=14, decimal_places=2, default=CERO)
    descuento_total = models.DecimalField(max_digits=14, decimal_places=2, default=CERO)
    base_gravada = models.DecimalField(max_digits=14, decimal_places=2, default=CERO)
    base_exenta = models.DecimalField(max_digits=14, decimal_places=2, default=CERO)
    itbms = models.DecimalField(max_digits=14, decimal_places=2, default=CERO)
    total = models.DecimalField(max_digits=14, decimal_places=2, default=CERO)

    estado = models.CharField(
        "Estado", max_length=10, choices=ESTADOS, default=ESTADO_EMITIDA
    )
    fecha_creacion = models.DateTimeField("Creada", auto_now_add=True)
    fecha_anulacion = models.DateTimeField("Anulada", blank=True, null=True)

    class Meta:
        verbose_name = "Factura"
        verbose_name_plural = "Facturas"
        ordering = ["-fecha", "-numero_serie"]

    def __str__(self):
        return f"{self.numero_serie} - {self.cliente_nombre}"

    @property
    def anulada(self):
        return self.estado == self.ESTADO_ANULADA

    @property
    def texto_condicion_pago(self):
        if self.condicion_pago == self.CONDICION_CREDITO:
            return "Crédito"
        return "Contado"

    @property
    def fecha_vencimiento(self):
        """Vencimiento: un anio calendario despues de la fecha de la factura."""
        fecha = self.fecha
        try:
            return fecha.replace(year=fecha.year + 1)
        except ValueError:
            return fecha.replace(year=fecha.year + 1, month=2, day=28)

    @property
    def total_en_letras(self):
        from facturacion.services.numero_a_letras import total_en_letras

        return total_en_letras(self.total)


class LineaFactura(models.Model):
    """Un producto dentro de una factura."""

    factura = models.ForeignKey(
        Factura, on_delete=models.CASCADE, related_name="lineas"
    )
    orden = models.PositiveIntegerField("Orden")
    descripcion = models.CharField("Descripcion", max_length=300)
    codigo_barras = models.CharField("Codigo de barras", max_length=100, blank=True)
    categoria = models.CharField("Categoria", max_length=120, blank=True)
    cantidad = models.DecimalField(
        "Cantidad", max_digits=14, decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    precio_unitario = models.DecimalField("Precio unitario", max_digits=14, decimal_places=2)
    descuento_pct = models.DecimalField(
        "Descuento %", max_digits=6, decimal_places=2, default=CERO
    )
    gravada = models.BooleanField("Gravada (ITBMS 7%)", default=True)
    # El precio se guarda por la CAJA completa; si cobrar_por es "unidad",
    # el monto divide entre las unidades que trae la caja.
    unidades_por_caja = models.PositiveIntegerField(
        "Unidades por caja", default=1,
        validators=[MinValueValidator(1)],
        help_text="Cuántas unidades trae la caja. El precio es por la caja.",
    )
    cobrar_por = models.CharField(
        "Cobrar por", max_length=10, choices=COBRAR_POR_OPCIONES,
        default=COBRAR_POR_UNIDAD,
    )
    monto = models.DecimalField("Monto", max_digits=14, decimal_places=2, default=CERO)

    class Meta:
        verbose_name = "Linea de factura"
        verbose_name_plural = "Lineas de factura"
        ordering = ["orden"]
        constraints = [
            models.UniqueConstraint(
                fields=["factura", "orden"], name="linea_factura_orden_unico"
            )
        ]

    @property
    def cantidad_texto(self):
        """Cantidad lista para mostrar: '12.00 und', '1.00 caja', '2.00 cajas'."""
        if self.cobrar_por == COBRAR_POR_CAJA:
            palabra = "caja" if self.cantidad == 1 else "cajas"
            return f"{self.cantidad:.2f} {palabra}"
        return f"{self.cantidad:.2f} und"

    @property
    def precio_efectivo_texto(self):
        """Precio efectivo listo para mostrar: '30.00 / caja' o '1.25 / und'."""
        precio = precio_efectivo(
            self.precio_unitario, self.unidades_por_caja, self.cobrar_por
        )
        sufijo = " / caja" if self.cobrar_por == COBRAR_POR_CAJA else " / und"
        return f"{formato_precio(precio)}{sufijo}"

    def __str__(self):
        return f"{self.factura.numero_serie} #{self.orden} {self.descripcion}"
