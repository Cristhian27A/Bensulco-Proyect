from django.contrib import admin

from facturacion.models import ConfiguracionNegocio, ContadorSerie, Factura, LineaFactura


@admin.register(ConfiguracionNegocio)
class ConfiguracionNegocioAdmin(admin.ModelAdmin):
    list_display = ("empresa_nombre", "empresa_ruc", "color_principal", "actualizado")
    readonly_fields = ("actualizado",)

    def has_add_permission(self, request):
        return not ConfiguracionNegocio.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ContadorSerie)
class ContadorSerieAdmin(admin.ModelAdmin):
    list_display = ("anio", "ultimo_numero")


class LineaFacturaInline(admin.TabularInline):
    model = LineaFactura
    extra = 0
    fields = (
        "orden", "descripcion", "codigo_barras", "categoria", "cantidad",
        "precio_unitario", "descuento_pct", "gravada", "monto",
    )
    readonly_fields = ("monto",)
    ordering = ("orden",)


@admin.register(Factura)
class FacturaAdmin(admin.ModelAdmin):
    list_display = (
        "numero_serie", "fecha", "cliente_nombre", "total", "estado", "fecha_creacion"
    )
    list_filter = ("estado", "fecha")
    search_fields = ("numero_serie", "cliente_nombre", "cliente_ruc")
    date_hierarchy = "fecha"
    inlines = [LineaFacturaInline]
    readonly_fields = ("numero_serie", "codigo_verificacion", "fecha_creacion")
