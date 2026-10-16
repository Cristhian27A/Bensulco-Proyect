"""Modelos del catalogo de productos y pedidos B2B."""

from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models

CERO = Decimal("0.00")


class Categoria(models.Model):
    """Categoria de productos del catalogo."""

    nombre = models.CharField("Nombre", max_length=100, unique=True)

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    """Producto del catalogo disponible para pedidos B2B."""

    ESTADO_ACTIVO = True
    ESTADO_INACTIVO = False

    ESTADO_OPCIONES = [
        (ESTADO_ACTIVO, "Activo"),
        (ESTADO_INACTIVO, "Inactivo"),
    ]

    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        verbose_name="Categoría",
        related_name="productos",
    )
    nombre = models.CharField("Nombre del producto", max_length=200)
    sku = models.CharField(
        "SKU",
        max_length=50,
        unique=True,
        help_text="Código único de identificación del producto",
    )
    descripcion_corta = models.CharField(
        "Descripción corta",
        max_length=500,
        help_text="Descripción breve para mostrar en el catálogo",
    )
    imagen = models.ImageField(
        "Imagen",
        upload_to="productos/",
        blank=True,
        null=True,
        help_text="Imagen del producto para el catálogo",
    )
    precio_caja = models.DecimalField(
        "Precio por caja",
        max_digits=14,
        decimal_places=2,
        validators=[MinValueValidator(CERO)],
        help_text="Precio de la caja completa",
    )
    precio_unidad = models.DecimalField(
        "Precio por unidad",
        max_digits=14,
        decimal_places=2,
        validators=[MinValueValidator(CERO)],
        help_text="Precio de una unidad suelta",
    )
    unidades_por_caja = models.PositiveIntegerField(
        "Unidades por caja",
        default=1,
        validators=[MinValueValidator(1)],
        help_text="Cuántas unidades trae la caja",
    )
    aplica_itbms = models.BooleanField(
        "Aplica ITBMS 7%",
        default=True,
        help_text="Si el producto está gravado con ITBMS",
    )
    estado_activo = models.BooleanField(
        "Estado activo",
        default=ESTADO_ACTIVO,
        choices=ESTADO_OPCIONES,
        help_text="Si el producto está disponible para pedidos",
    )
    fecha_creacion = models.DateTimeField("Creado", auto_now_add=True)
    fecha_actualizacion = models.DateTimeField("Actualizado", auto_now=True)

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ["categoria", "nombre"]

    def __str__(self):
        return f"{self.sku} - {self.nombre}"

    @property
    def precio_efectivo_por_unidad(self):
        """Precio por unidad calculado (precio_caja / unidades_por_caja)."""
        if self.unidades_por_caja > 0:
            return self.precio_caja / self.unidades_por_caja
        return self.precio_unidad


class ClienteB2B(models.Model):
    """Cliente B2B que puede hacer pedidos a través del portal."""

    nombre_empresa = models.CharField("Nombre de la empresa", max_length=200)
    ruc = models.CharField("RUC / DV", max_length=40, unique=True)
    email_contacto = models.EmailField("Email de contacto")
    telefono = models.CharField("Teléfono", max_length=60, blank=True)
    direccion = models.TextField("Dirección", blank=True)
    fecha_registro = models.DateTimeField("Fecha de registro", auto_now_add=True)
    activo = models.BooleanField("Activo", default=True)

    class Meta:
        verbose_name = "Cliente B2B"
        verbose_name_plural = "Clientes B2B"
        ordering = ["nombre_empresa"]

    def __str__(self):
        return f"{self.nombre_empresa} ({self.ruc})"


class PedidoB2B(models.Model):
    """Pedido realizado por un cliente B2B a través del portal."""

    ESTADO_PENDIENTE = "pendiente"
    ESTADO_PROCESANDO = "procesando"
    ESTADO_FACTURADO = "facturado"
    ESTADO_CANCELADO = "cancelado"

    ESTADO_OPCIONES = [
        (ESTADO_PENDIENTE, "Pendiente"),
        (ESTADO_PROCESANDO, "Procesando"),
        (ESTADO_FACTURADO, "Facturado"),
        (ESTADO_CANCELADO, "Cancelado"),
    ]

    cliente = models.ForeignKey(
        ClienteB2B,
        on_delete=models.PROTECT,
        verbose_name="Cliente",
        related_name="pedidos",
    )
    fecha_creacion = models.DateTimeField("Fecha de creación", auto_now_add=True)
    fecha_actualizacion = models.DateTimeField("Actualizado", auto_now=True)
    estado = models.CharField(
        "Estado",
        max_length=20,
        choices=ESTADO_OPCIONES,
        default=ESTADO_PENDIENTE,
    )
    total_estimado = models.DecimalField(
        "Total estimado",
        max_digits=14,
        decimal_places=2,
        default=CERO,
    )
    notas = models.TextField("Notas del cliente", blank=True)
    # Para relacionar con la factura cuando se procese
    factura_generada = models.ForeignKey(
        "facturacion.Factura",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Factura generada",
        related_name="pedido_origen",
    )

    class Meta:
        verbose_name = "Pedido B2B"
        verbose_name_plural = "Pedidos B2B"
        ordering = ["-fecha_creacion"]

    def __str__(self):
        return f"Pedido #{self.pk} - {self.cliente.nombre_empresa} ({self.get_estado_display()})"

    @property
    def pendiente(self):
        return self.estado == self.ESTADO_PENDIENTE

    @property
    def puede_facturarse(self):
        return self.estado in [self.ESTADO_PENDIENTE, self.ESTADO_PROCESANDO]


class LineaPedidoB2B(models.Model):
    """Una línea de producto dentro de un pedido B2B."""

    pedido = models.ForeignKey(
        PedidoB2B,
        on_delete=models.CASCADE,
        verbose_name="Pedido",
        related_name="lineas",
    )
    producto = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT,
        verbose_name="Producto",
        related_name="lineas_pedido",
    )
    cantidad_cajas = models.DecimalField(
        "Cantidad en cajas",
        max_digits=14,
        decimal_places=2,
        default=CERO,
        validators=[MinValueValidator(CERO)],
    )
    cantidad_unidades = models.DecimalField(
        "Cantidad en unidades",
        max_digits=14,
        decimal_places=2,
        default=CERO,
        validators=[MinValueValidator(CERO)],
    )
    subtotal = models.DecimalField(
        "Subtotal",
        max_digits=14,
        decimal_places=2,
        default=CERO,
    )
    orden = models.PositiveIntegerField("Orden", default=0)

    class Meta:
        verbose_name = "Línea de pedido B2B"
        verbose_name_plural = "Líneas de pedido B2B"
        ordering = ["orden"]
        constraints = [
            models.UniqueConstraint(
                fields=["pedido", "orden"], name="linea_pedido_orden_unico"
            )
        ]

    def __str__(self):
        return f"{self.pedido.pk} - {self.producto.nombre}"

    @property
    def cantidad_total_unidades(self):
        """Total de unidades sumando cajas y unidades sueltas."""
        return self.cantidad_unidades + (self.cantidad_cajas * self.producto.unidades_por_caja)

    def calcular_subtotal(self):
        """Calcula el subtotal de la línea basado en el precio del producto."""
        # Subtotal = (cajas * precio_caja) + (unidades * precio_unidad)
        subtotal_cajas = self.cantidad_cajas * self.producto.precio_caja
        subtotal_unidades = self.cantidad_unidades * self.producto.precio_unidad
        self.subtotal = subtotal_cajas + subtotal_unidades
        self.save(update_fields=["subtotal"])
        return self.subtotal
