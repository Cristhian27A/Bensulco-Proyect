"""Configuración del admin para los modelos del catálogo."""

from django.contrib import admin
from django.utils.html import format_html

from .models import Categoria, ClienteB2B, LineaPedidoB2B, PedidoB2B, Producto


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ["nombre"]
    search_fields = ["nombre"]
    ordering = ["nombre"]


class LineaPedidoB2BInline(admin.TabularInline):
    model = LineaPedidoB2B
    extra = 0
    readonly_fields = ["subtotal"]
    fields = ["producto", "tipo_empaque", "cantidad", "subtotal", "orden"]


@admin.register(PedidoB2B)
class PedidoB2BAdmin(admin.ModelAdmin):
    list_display = [
        "pk",
        "cliente",
        "fecha_creacion",
        "estado",
        "total_estimado",
        "factura_generada",
    ]
    list_filter = ["estado", "fecha_creacion"]
    search_fields = ["cliente__nombre_empresa", "cliente__ruc"]
    readonly_fields = ["fecha_creacion", "fecha_actualizacion", "total_estimado"]
    inlines = [LineaPedidoB2BInline]
    date_hierarchy = "fecha_creacion"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("cliente", "factura_generada")


@admin.register(ClienteB2B)
class ClienteB2BAdmin(admin.ModelAdmin):
    list_display = ["nombre_empresa", "ruc", "email_contacto", "telefono", "activo"]
    list_filter = ["activo", "fecha_registro"]
    search_fields = ["nombre_empresa", "ruc", "email_contacto"]
    readonly_fields = ["fecha_registro"]


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = [
        "sku",
        "nombre",
        "categoria",
        "precio_caja",
        "precio_media_caja",
        "precio_unidad",
        "precio_consumidor",
        "unidades_por_caja",
        "permite_media_caja",
        "estado_activo",
        "vista_previa_imagen",
    ]
    list_filter = ["categoria", "estado_activo", "aplica_itbms", "permite_media_caja"]
    search_fields = ["nombre", "sku", "descripcion_corta"]
    readonly_fields = ["fecha_creacion", "fecha_actualizacion", "vista_previa_imagen"]
    list_editable = ["estado_activo"]
    fieldsets = (
        (None, {
            "fields": ("categoria", "nombre", "sku", "codigo_barras", "descripcion_corta", "imagen")
        }),
        ("Precios", {
            "fields": ("precio_caja", "precio_media_caja", "precio_unidad", "precio_consumidor", "unidades_por_caja")
        }),
        ("Configuración", {
            "fields": ("aplica_itbms", "permite_media_caja", "estado_activo")
        }),
        ("Fechas", {
            "fields": ("fecha_creacion", "fecha_actualizacion", "vista_previa_imagen"),
            "classes": ("collapse",)
        }),
    )

    class Media:
        js = ("catalogo/js/admin_producto.js",)

    def vista_previa_imagen(self, obj):
        if obj.imagen:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover;" />',
                obj.imagen.url,
            )
        return "Sin imagen"

    vista_previa_imagen.short_description = "Imagen"
