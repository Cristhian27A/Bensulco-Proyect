"""Cambios pedidos por el cliente: sin descuentos, notas unicas y dos colores.

Esta migracion mueve los datos existentes a los campos nuevos antes de quitar
los viejos, para que no se pierda el texto de las facturas ya emitidas.
"""

from django.db import migrations, models


def copiar_notas(apps, esquema):
    """Pasa "Tenga en cuenta" y "notas extra" al unico campo de notas."""
    Factura = apps.get_model("facturacion", "Factura")
    ConfiguracionNegocio = apps.get_model("facturacion", "ConfiguracionNegocio")

    for factura in Factura.objects.all().iterator():
        partes = [
            (factura.observaciones or "").strip(),
            (factura.notas_extra or "").strip(),
        ]
        texto = "\n".join(parte for parte in partes if parte)
        if texto != (factura.observaciones or ""):
            factura.notas = texto
            factura.save(update_fields=["notas"])

    for configuracion in ConfiguracionNegocio.objects.all().iterator():
        texto = (configuracion.tenga_en_cuenta or "").strip()
        if texto:
            configuracion.notas_predeterminadas = texto
            configuracion.save(update_fields=["notas_predeterminadas"])


def no_fazer_nada(apps, esquema):
    """La operacion inversa no restituye los campos viejos."""


class Migration(migrations.Migration):

    dependencies = [
        ("facturacion", "0001_initial"),
    ]

    operations = [
        # Primero se crean los destinos.
        migrations.AddField(
            model_name="configuracionnegocio",
            name="color_barra_factura",
            field=models.CharField(
                default="#5B3A9E", max_length=7,
                verbose_name="Color de la barra FACTURA",
                help_text="Franja del titulo de la factura en el PDF.",
            ),
        ),
        migrations.AddField(
            model_name="configuracionnegocio",
            name="color_tabla",
            field=models.CharField(
                default="#3A0088", max_length=7,
                verbose_name="Color de la tabla y los totales",
                help_text="Encabezado de la tabla y banda del gran total.",
            ),
        ),
        migrations.AddField(
            model_name="configuracionnegocio",
            name="notas_predeterminadas",
            field=models.TextField(
                blank=True,
                verbose_name="Texto de notas por defecto",
                help_text="Se precarga en cada factura nueva y se puede editar o borrar.",
            ),
        ),
        migrations.AddField(
            model_name="factura",
            name="notas",
            field=models.TextField(blank=True, verbose_name="Notas"),
        ),
        # Luego se copian los datos y se sueltan los campos viejos.
        migrations.RunPython(copiar_notas, no_fazer_nada),
        migrations.RemoveField(
            model_name="configuracionnegocio", name="tenga_en_cuenta",
        ),
        migrations.RemoveField(model_name="factura", name="notas_extra"),
        migrations.RemoveField(model_name="factura", name="observaciones"),
    ]
