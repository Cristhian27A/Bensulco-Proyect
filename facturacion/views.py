"""Vistas de la facturacion."""

from datetime import date
from decimal import Decimal

from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from django.db.models.functions import Coalesce
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_GET, require_POST

from facturacion.forms import (
    ConfiguracionForm,
    FacturaForm,
    FiltroHistorialForm,
    LineaFacturaFormSet,
)
from facturacion.models import ConfiguracionNegocio, Factura
from facturacion.services import serie as servicio_serie
from facturacion.services import pdf as servicio_pdf
from facturacion.services import totales as servicio_totales

D = Decimal

CANTIDAD_POR_PAGINA = 20
CERO = Decimal("0.00")


def _configuracion():
    return ConfiguracionNegocio.cargar()


def _datos_para_formulario(factura: Factura) -> dict:
    """Arma el diccionario inicial del formulario para duplicar una factura."""
    datos = {
        "cliente_nombre": factura.cliente_nombre,
        "cliente_ruc": factura.cliente_ruc,
        "mostrar_ruc": factura.mostrar_ruc,
        "cliente_direccion": factura.cliente_direccion,
        "cliente_telefono": factura.cliente_telefono,
        "cliente_correo": factura.cliente_correo,
        "sucursal": factura.sucursal,
        "vendedor": factura.vendedor,
        "fecha": date.today().isoformat(),
        "condicion_pago": factura.condicion_pago,
        "aplicar_itbms": True,
        "notas": factura.notas,
    }
    lineas = []
    for linea in factura.lineas.all():
        lineas.append({
            "descripcion": linea.descripcion,
            "codigo_barras": linea.codigo_barras,
            "categoria": linea.categoria,
            "cantidad": str(linea.cantidad),
            "precio_unitario": str(linea.precio_unitario),
            "gravada": linea.gravada,
            "unidades_por_caja": linea.unidades_por_caja,
            "cobrar_por": linea.cobrar_por,
        })
    # En la sesion se guarda el pk: la sesion se serializa a JSON.
    return {"factura": datos, "lineas": lineas, "duplicada_de": factura.pk}


def nueva_factura(request):
    """Pantalla de inicio: el formulario para crear una factura."""
    configuracion = _configuracion()
    duplicada_de = None

    if request.method == "POST":
        form = FacturaForm(request.POST)
        formset = LineaFacturaFormSet(request.POST, prefix="linea")

        if form.is_valid() and formset.is_valid():
            aplicar_itbms = form.cleaned_data.get("aplicar_itbms", False)
            lineas = []
            for form_linea in formset.forms:
                if not form_linea.has_changed():
                    continue
                datos = form_linea.cleaned_data
                if not (datos.get("descripcion") or "").strip():
                    continue
                lineas.append({
                    "descripcion": datos["descripcion"].strip(),
                    "codigo_barras": (datos.get("codigo_barras") or "").strip(),
                    "categoria": (datos.get("categoria") or "").strip(),
                    "cantidad": datos.get("cantidad") or 0,
                    "precio_unitario": datos.get("precio_unitario") or 0,
                    "gravada": True if aplicar_itbms else datos.get("gravada", True),
                    "unidades_por_caja": datos.get("unidades_por_caja") or 1,
                    "cobrar_por": datos.get("cobrar_por") or servicio_totales.COBRAR_POR_UNIDAD,
                })

            if not lineas:
                messages.error(
                    request,
                    "Agrega al menos un producto con descripción, cantidad y precio.",
                )
            elif any(
                D(linea["cantidad"] or 0) <= 0
                or D(linea["precio_unitario"] or 0) <= 0
                for linea in lineas
            ):
                messages.error(
                    request,
                    "Cada producto necesita una cantidad y un precio mayores que cero.",
                )
            else:
                factura = servicio_serie.crear_factura(
                    {
                        "fecha": form.cleaned_data["fecha"],
                        "cliente_nombre": form.cleaned_data["cliente_nombre"].strip(),
                        "cliente_ruc": form.cleaned_data.get("cliente_ruc", ""),
                        "mostrar_ruc": form.cleaned_data.get("mostrar_ruc", True),
                        "cliente_direccion": form.cleaned_data.get("cliente_direccion", ""),
                        "cliente_telefono": form.cleaned_data.get("cliente_telefono", ""),
                        "cliente_correo": form.cleaned_data.get("cliente_correo", ""),
                        "sucursal": form.cleaned_data.get("sucursal", ""),
                        "vendedor": form.cleaned_data.get("vendedor", ""),
                        "condicion_pago": form.cleaned_data["condicion_pago"],
                        "orden_compra": form.cleaned_data.get("orden_compra", ""),
                        "notas": form.cleaned_data.get("notas", ""),
                        "itbms_activo": aplicar_itbms,
                    },
                    lineas,
                )
                messages.success(
                    request,
                    f"Factura {factura.numero_serie} creada por {factura.total:,.2f}.",
                )
                return redirect("facturacion:detalle", pk=factura.pk)

            messages.error(
                request, "Revisa los datos marcados para poder generar la factura."
            )
    else:
        prellenado = request.session.pop("factura_prellenada", None)
        if prellenado:
            form = FacturaForm(initial=prellenado["factura"])
            formset = LineaFacturaFormSet(
                initial=prellenado["lineas"], prefix="linea",
            )
            duplicada_de = prellenado.get("duplicada_de")
            if duplicada_de:
                duplicada_de = Factura.objects.filter(pk=duplicada_de).first()
        else:
            form = FacturaForm(initial={
                "fecha": date.today().isoformat(),
                "condicion_pago": Factura.CONDICION_CONTADO,
                "aplicar_itbms": True,
                # Precarga las notas por defecto; se pueden borrar o editar.
                "notas": configuracion.notas_predeterminadas,
            })
            formset = LineaFacturaFormSet(prefix="linea")

    return render(
        request,
        "facturacion/factura_form.html",
        {
            "form": form,
            "formset": formset,
            "configuracion": configuracion,
            "duplicada_de": duplicada_de,
        },
    )


@require_GET
def duplicar_factura(request, pk):
    """Abre el formulario precargado con los datos de una factura existente."""
    factura = get_object_or_404(
        Factura.objects.prefetch_related("lineas"), pk=pk
    )
    request.session["factura_prellenada"] = _datos_para_formulario(factura)
    return redirect("facturacion:nueva")


def historial(request):
    """Tabla de facturas con búsqueda, filtros y paginación."""
    form = FiltroHistorialForm(request.GET or None)
    facturas = Factura.objects.all()

    if form.is_valid():
        datos = form.cleaned_data
        if datos.get("q"):
            texto = datos["q"]
            facturas = facturas.filter(
                Q(cliente_nombre__icontains=texto)
                | Q(numero_serie__icontains=texto)
                | Q(cliente_ruc__icontains=texto)
            )
        if datos.get("desde"):
            facturas = facturas.filter(fecha__gte=datos["desde"])
        if datos.get("hasta"):
            facturas = facturas.filter(fecha__lte=datos["hasta"])
        if datos.get("estado"):
            facturas = facturas.filter(estado=datos["estado"])

    paginador = Paginator(facturas, CANTIDAD_POR_PAGINA)
    pagina = paginador.get_page(request.GET.get("pagina"))

    # Suma de lo emitido dentro del filtro actual (las anuladas no cuentan).
    suma_total = facturas.filter(estado=Factura.ESTADO_EMITIDA).aggregate(
        valor=Coalesce(Sum("total"), CERO)
    )["valor"]

    return render(
        request,
        "facturacion/historial.html",
        {
            "form": form,
            "pagina": pagina,
            "paginador": paginador,
            "total_facturas": paginador.count,
            "suma_total": suma_total,
        },
    )


def detalle_factura(request, pk):
    """Resumen legible de una factura, con el PDF en pantalla."""
    factura = get_object_or_404(Factura.objects.prefetch_related("lineas"), pk=pk)
    lineas = factura.lineas.all()
    total = factura.total
    return render(
        request,
        "facturacion/factura_detalle.html",
        {
            "factura": factura,
            "lineas": lineas,
            "total_letras": factura.total_en_letras,
            "configuracion": _configuracion(),
        },
    )


@require_GET
def factura_pdf(request, pk):
    """Descarga (o muestra) el PDF de la factura."""
    from facturacion.services.pdf import generar_pdf, nombre_archivo_pdf

    factura = get_object_or_404(Factura.objects.prefetch_related("lineas"), pk=pk)
    contenido = generar_pdf(factura)

    respuesta = HttpResponse(contenido, content_type="application/pdf")
    nombre = nombre_archivo_pdf(factura)
    disposicion = "inline" if request.GET.get("ver") == "1" else "attachment"
    respuesta["Content-Disposition"] = f'{disposicion}; filename="{nombre}"'
    return respuesta


@require_POST
def anular_factura(request, pk):
    """Anula una factura. Una factura emitida no se edita nunca."""
    factura = get_object_or_404(Factura, pk=pk)
    if factura.estado == Factura.ESTADO_ANULADA:
        messages.warning(request, f"La factura {factura.numero_serie} ya estaba anulada.")
    else:
        servicio_serie.anular_factura(factura)
        messages.success(
            request, f"Factura {factura.numero_serie} anulada."
        )
    return redirect(reverse("facturacion:detalle", args=[factura.pk]))


def configuracion(request):
    """Página única con los datos del negocio."""
    configuracion = _configuracion()
    if request.method == "POST":
        form = ConfiguracionForm(request.POST, request.FILES, instance=configuracion)
        if form.is_valid():
            form.save()
            messages.success(request, "Configuración guardada.")
            return redirect("facturacion:configuracion")
        messages.error(request, "Revisa los datos marcados.")
    else:
        form = ConfiguracionForm(instance=configuracion)

    return render(
        request,
        "facturacion/configuracion.html",
        {"form": form, "configuracion": configuracion},
    )


def verificar(request, serie, codigo):
    """Comprueba una factura con el número de serie y el código del QR."""
    serie = (serie or "").upper().strip()
    codigo = (codigo or "").upper().strip()
    factura = Factura.objects.filter(numero_serie=serie).first()

    valida = bool(
        factura
        and servicio_serie.verificar_codigo(
            factura.numero_serie, codigo, factura.total, factura.fecha
        )
    )

    if valida and factura.estado == Factura.ESTADO_ANULADA:
        mensaje_estado = "Esta factura fue anulada."
        tipo = "anulada"
    elif valida:
        mensaje_estado = "El código coincide con la factura registrada."
        tipo = "valida"
    elif factura:
        mensaje_estado = "El código no coincide con esta factura."
        tipo = "invalida"
    else:
        mensaje_estado = "No existe ninguna factura con ese número de serie."
        tipo = "invalida"

    return render(
        request,
        "facturacion/verificar.html",
        {
            "factura": factura if valida else None,
            "no_valida": factura if (factura and not valida) else None,
            "valida": valida,
            "tipo": tipo,
            "mensaje": mensaje_estado,
            "serie": serie,
            "codigo": codigo,
        },
    )
