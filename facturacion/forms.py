"""Formularios de la facturacion."""

import re
from decimal import Decimal

from django import forms
from django.forms import formset_factory

from facturacion.models import (
    COBRAR_POR_OPCIONES,
    COBRAR_POR_UNIDAD,
    ConfiguracionNegocio,
    Factura,
    LineaFactura,
)

CERO = Decimal("0.00")
CIENTO = Decimal("100")

#: Un color de la configuracion: #rgb o #rrggbb.
COLOR_VALIDO = re.compile(r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})$")


class FacturaForm(forms.Form):
    """Datos del cliente y datos de la factura."""

    cliente_nombre = forms.CharField(
        label="Nombre del cliente",
        max_length=200,
        widget=forms.TextInput(attrs={"placeholder": "Nombre o razón social", "autofocus": True}),
    )
    cliente_ruc = forms.CharField(
        label="RUC / DV", max_length=40, required=False,
        widget=forms.TextInput(attrs={"placeholder": "1-2345678-90-123"}),
    )
    cliente_direccion = forms.CharField(
        label="Dirección", max_length=250, required=False,
        widget=forms.TextInput(attrs={"placeholder": "Dirección del cliente"}),
    )
    cliente_telefono = forms.CharField(
        label="Teléfono", max_length=60, required=False,
        widget=forms.TextInput(attrs={"placeholder": "Teléfono"}),
    )
    cliente_correo = forms.EmailField(
        label="Correo", required=False,
        widget=forms.EmailInput(attrs={"placeholder": "correo@cliente.com"}),
    )
    sucursal = forms.CharField(
        label="Comprar desde", max_length=150, required=False,
        widget=forms.TextInput(attrs={"placeholder": "Sucursal o tienda"}),
    )
    orden_compra = forms.CharField(
        label="Orden de compra", required=False, max_length=60,
        widget=forms.TextInput(attrs={
            "placeholder": "Déjala vacía para asignar una automática",
        }),
    )
    mostrar_ruc = forms.BooleanField(
        label="Mostrar RUC/DV en la factura",
        required=False, initial=True,
    )
    vendedor = forms.CharField(
        label="Realizado por / vendedor", max_length=150, required=False,
        widget=forms.TextInput(attrs={"placeholder": "Nombre del vendedor"}),
    )
    fecha = forms.DateField(
        label="Fecha",
        widget=forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
    )
    condicion_pago = forms.ChoiceField(
        label="Condición de pago",
        choices=Factura.CONDICIONES_PAGO,
        widget=forms.Select(),
    )
    aplicar_itbms = forms.BooleanField(
        label="Aplicar ITBMS 7% a todos los productos",
        required=False, initial=True,
    )
    notas = forms.CharField(
        label="Notas", required=False,
        help_text="Notas de esta factura. Se imprimen en el PDF, abajo a la izquierda.",
        widget=forms.Textarea(attrs={"rows": 4, "placeholder": "Notas de la factura"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for campo in self.fields.values():
            if isinstance(campo.widget, (forms.CheckboxInput, forms.Select)):
                continue
            campo.widget.attrs.setdefault("class", "campo")


class LineaFacturaForm(forms.Form):
    """Un producto dentro de la factura."""

    # Las filas que el usuario deja en blanco se ignoran, en vez de fallar.
    empty_permitted = True

    descripcion = forms.CharField(
        label="Producto", max_length=300, required=False,
        widget=forms.TextInput(attrs={"placeholder": "Descripción del producto"}),
    )
    codigo_barras = forms.CharField(
        label="Código de barras", max_length=100, required=False,
        widget=forms.TextInput(attrs={"placeholder": "Código", "class": "campo-pequeno"}),
    )
    cantidad = forms.DecimalField(
        label="Cantidad", required=False, min_value=CERO, max_digits=14, decimal_places=2,
        widget=forms.NumberInput(attrs={"step": "0.01", "min": "0", "class": "campo-numero js-cantidad"}),
    )
    precio_unitario = forms.DecimalField(
        label="Precio caja", required=False, min_value=CERO, max_digits=14,
        decimal_places=2,
        widget=forms.NumberInput(attrs={"step": "0.01", "min": "0", "class": "campo-numero js-precio"}),
    )
    precio_unidad = forms.DecimalField(
        label="Precio unidad", required=False, min_value=CERO, max_digits=14,
        decimal_places=2,
        widget=forms.NumberInput(attrs={"step": "0.01", "min": "0", "class": "campo-numero js-precio-unidad"}),
    )
    unidades_por_caja = forms.IntegerField(
        label="Unidades por caja", required=False, min_value=1, initial=1,
        widget=forms.NumberInput(attrs={"min": "1", "step": "1", "class": "campo-numero js-upxc"}),
    )
    cobrar_por = forms.ChoiceField(
        label="Cobrar por", required=False,
        choices=COBRAR_POR_OPCIONES, initial=COBRAR_POR_UNIDAD,
        widget=forms.Select(attrs={"class": "js-cobrar-por"}),
    )
    # El descuento sigue en el modelo (siempre 0) pero ya no se pide: la
    # factura se emite al precio unitario sin descuento.
    gravada = forms.BooleanField(
        label="Gravada", required=False,
        widget=forms.CheckboxInput(attrs={"class": "js-gravada"}),
    )


LineaFacturaFormSet = formset_factory(
    LineaFacturaForm,
    extra=1,
    can_delete=False,
    max_num=100,
)


class ConfiguracionForm(forms.ModelForm):
    """Datos del negocio que alimentan el encabezado del PDF."""

    class Meta:
        model = ConfiguracionNegocio
        fields = [
            "empresa_nombre", "empresa_ruc", "mostrar_ruc", "empresa_direccion",
            "empresa_correo", "empresa_telefono", "logo", "color_principal",
            "color_barra_factura", "color_tabla", "datos_bancarios",
            "notas_predeterminadas",
        ]
        widgets = {
            "empresa_nombre": forms.TextInput(attrs={"class": "campo", "autofocus": True}),
            "empresa_ruc": forms.TextInput(attrs={"class": "campo"}),
            "empresa_direccion": forms.Textarea(attrs={"class": "campo", "rows": 2}),
            "empresa_correo": forms.EmailInput(attrs={"class": "campo"}),
            "empresa_telefono": forms.TextInput(attrs={"class": "campo"}),
            "datos_bancarios": forms.Textarea(attrs={"class": "campo", "rows": 3}),
            "notas_predeterminadas": forms.Textarea(attrs={"class": "campo", "rows": 4}),
        }
        labels = {
            "empresa_nombre": "Nombre de la empresa",
            "empresa_ruc": "RUC / DV",
            "mostrar_ruc": "Mostrar RUC/DV en el encabezado y en el pie",
            "empresa_direccion": "Dirección",
            "empresa_correo": "Correo",
            "empresa_telefono": "Teléfono",
            "logo": "Logo",
            "color_principal": "Color principal de la marca",
            "color_barra_factura": "Color de la barra ORDEN DE COMPRA",
            "color_tabla": "Color de la tabla y los totales",
            "datos_bancarios": "Datos bancarios",
            "notas_predeterminadas": "Texto de notas por defecto",
        }

    #: Campos que son selectores de color, no cajas de texto.
    COLORES = (
        "color_principal", "color_barra_factura", "color_tabla",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for nombre, campo in self.fields.items():
            if nombre in self.COLORES:
                campo.widget = forms.TextInput(
                    attrs={"type": "color", "class": "campo-color"}
                )
                campo.required = False
                continue
            campo.widget.attrs.setdefault("class", "campo")

    def clean(self):
        limpio = super().clean()
        for nombre in self.COLORES:
            valor = limpio.get(nombre)
            if valor and not COLOR_VALIDO.match(valor):
                limpio[nombre] = self.errors.get(nombre)
                self.add_error(
                    nombre,
                    "Escriba un color hexadecimal, por ejemplo #3A0088.",
                )
        return limpio


class FiltroHistorialForm(forms.Form):
    """Búsqueda del historial."""

    q = forms.CharField(
        label="Buscar", required=False, max_length=100,
        widget=forms.TextInput(
            attrs={"placeholder": "Cliente o número de serie", "class": "campo-buscar"}
        ),
    )
    desde = forms.DateField(
        label="Desde", required=False,
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    hasta = forms.DateField(
        label="Hasta", required=False,
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    estado = forms.ChoiceField(
        label="Estado", required=False,
        choices=[("", "Todos"), (Factura.ESTADO_EMITIDA, "Emitidas"),
                 (Factura.ESTADO_ANULADA, "Anuladas")],
    )
