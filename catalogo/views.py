"""Vistas públicas del catálogo y pedidos B2B."""

from decimal import Decimal

from django.contrib import messages
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from catalogo.models import Categoria, ClienteB2B, LineaPedidoB2B, PedidoB2B, Producto
from facturacion.services.pdf import generar_pdf
from facturacion.services.numero_a_letras import total_en_letras

CERO = Decimal("0.00")


def catalogo_publico(request):
    """Página pública del catálogo de productos (optimizada para móviles)."""
    categoria_id = request.GET.get("categoria")
    busqueda = request.GET.get("q", "").strip()

    productos = Producto.objects.filter(estado_activo=True).select_related("categoria")

    if categoria_id:
        productos = productos.filter(categoria_id=categoria_id)

    if busqueda:
        productos = productos.filter(
            Q(nombre__icontains=busqueda)
            | Q(sku__icontains=busqueda)
            | Q(descripcion_corta__icontains=busqueda)
        )

    categorias = Categoria.objects.all()
    carrito = request.session.get("carrito", {})

    # Calcular total del carrito
    total_carrito = CERO
    for item in carrito.values():
        total_carrito += Decimal(item.get("subtotal", "0"))

    return render(
        request,
        "catalogo/catalogo.html",
        {
            "productos": productos,
            "categorias": categorias,
            "categoria_activa": int(categoria_id) if categoria_id else None,
            "busqueda": busqueda,
            "carrito": carrito,
            "total_carrito": total_carrito,
            "cantidad_items": len(carrito),
        },
    )


def agregar_al_carrito(request):
    """Agrega un producto al carrito de compras (sesión)."""
    if request.method != "POST":
        return redirect("catalogo:catalogo")

    producto_id = request.POST.get("producto_id")
    cantidad_cajas = Decimal(request.POST.get("cantidad_cajas", "0"))
    cantidad_unidades = Decimal(request.POST.get("cantidad_unidades", "0"))

    if not producto_id:
        messages.error(request, "Producto no válido.")
        return redirect("catalogo:catalogo")

    producto = get_object_or_404(Producto, pk=producto_id, estado_activo=True)

    if cantidad_cajas <= CERO and cantidad_unidades <= CERO:
        messages.error(request, "Debe agregar al menos una cantidad.")
        return redirect("catalogo:catalogo")

    # Obtener o crear el carrito en la sesión
    carrito = request.session.get("carrito", {})

    # Calcular subtotal
    subtotal = (cantidad_cajas * producto.precio_caja) + (
        cantidad_unidades * producto.precio_unidad
    )

    # Agregar al carrito
    carrito[str(producto_id)] = {
        "producto_id": producto_id,
        "nombre": producto.nombre,
        "sku": producto.sku,
        "cantidad_cajas": str(cantidad_cajas),
        "cantidad_unidades": str(cantidad_unidades),
        "precio_caja": str(producto.precio_caja),
        "precio_unidad": str(producto.precio_unidad),
        "unidades_por_caja": producto.unidades_por_caja,
        "subtotal": str(subtotal),
    }

    request.session["carrito"] = carrito
    messages.success(request, f"{producto.nombre} agregado al carrito.")

    return redirect("catalogo:catalogo")


def eliminar_del_carrito(request, producto_id):
    """Elimina un producto del carrito."""
    carrito = request.session.get("carrito", {})

    if str(producto_id) in carrito:
        del carrito[str(producto_id)]
        request.session["carrito"] = carrito
        messages.success(request, "Producto eliminado del carrito.")

    return redirect("catalogo:catalogo")


def vaciar_carrito(request):
    """Vacía todo el carrito."""
    if "carrito" in request.session:
        del request.session["carrito"]
    messages.success(request, "Carrito vaciado.")
    return redirect("catalogo:catalogo")


def formulario_pedido(request):
    """Formulario para cerrar el pedido e ingresar datos del cliente."""
    carrito = request.session.get("carrito", {})

    if not carrito:
        messages.warning(request, "El carrito está vacío.")
        return redirect("catalogo:catalogo")

    clientes = ClienteB2B.objects.filter(activo=True)

    # Calcular total del carrito
    total = CERO
    for item in carrito.values():
        total += Decimal(item.get("subtotal", "0"))

    if request.method == "POST":
        # Procesar el pedido
        ruc = request.POST.get("ruc", "").strip()
        nombre_empresa = request.POST.get("nombre_empresa", "").strip()
        email = request.POST.get("email", "").strip()
        telefono = request.POST.get("telefono", "").strip()
        notas = request.POST.get("notas", "").strip()

        # Buscar o crear cliente
        if ruc:
            cliente = ClienteB2B.objects.filter(ruc=ruc).first()
            if not cliente:
                # Crear nuevo cliente
                cliente = ClienteB2B.objects.create(
                    nombre_empresa=nombre_empresa or "Cliente nuevo",
                    ruc=ruc,
                    email_contacto=email,
                    telefono=telefono,
                )
        else:
            messages.error(request, "Debe ingresar el RUC.")
            return render(
                request,
                "catalogo/formulario_pedido.html",
                {
                    "carrito": carrito,
                    "total": total,
                    "clientes": clientes,
                },
            )

        # Crear el pedido con transaction.atomic
        try:
            with transaction.atomic():
                pedido = PedidoB2B.objects.create(
                    cliente=cliente,
                    estado=PedidoB2B.ESTADO_PENDIENTE,
                    total_estimado=total,
                    notas=notas,
                )

                # Crear las líneas del pedido
                for orden, (prod_id, item) in enumerate(carrito.items(), start=1):
                    producto = Producto.objects.get(pk=prod_id)
                    cantidad_cajas = Decimal(item["cantidad_cajas"])
                    cantidad_unidades = Decimal(item["cantidad_unidades"])
                    subtotal = Decimal(item["subtotal"])

                    LineaPedidoB2B.objects.create(
                        pedido=pedido,
                        producto=producto,
                        cantidad_cajas=cantidad_cajas,
                        cantidad_unidades=cantidad_unidades,
                        subtotal=subtotal,
                        orden=orden,
                    )

            # Vaciar el carrito
            del request.session["carrito"]

            messages.success(
                request,
                f"Pedido enviado exitosamente. Su número es PED-{pedido.pk:04d}",
            )
            return redirect("catalogo:pedido_exitoso", pedido_id=pedido.pk)

        except Exception as e:
            messages.error(request, f"Error al crear el pedido: {str(e)}")
            return render(
                request,
                "catalogo/formulario_pedido.html",
                {
                    "carrito": carrito,
                    "total": total,
                    "clientes": clientes,
                },
            )

    return render(
        request,
        "catalogo/formulario_pedido.html",
        {
            "carrito": carrito,
            "total": total,
            "clientes": clientes,
        },
    )


def pedido_exitoso(request, pedido_id):
    """Pantalla de éxito después de enviar un pedido."""
    pedido = get_object_or_404(PedidoB2B, pk=pedido_id)

    return render(
        request,
        "catalogo/pedido_exitoso.html",
        {
            "pedido": pedido,
            "lineas": pedido.lineas.all().select_related("producto"),
        },
    )


def pdf_pedido(request, pedido_id):
    """Genera y descarga el PDF de un pedido."""
    pedido = get_object_or_404(PedidoB2B, pk=pedido_id)

    # Crear una factura temporal para reutilizar la lógica de PDF
    # NOTA: Esto es una solución temporal. En producción, deberíamos
    # crear un servicio específico para generar PDFs de pedidos.
    from facturacion.models import Factura, LineaFactura

    from facturacion.services.serie import (
        COBRAR_POR_CAJA,
        COBRAR_POR_UNIDAD,
    )

    # Crear factura temporal (no se guarda en DB)
    factura_temp = Factura(
        numero_serie=f"PED-{pedido.pk:04d}",
        codigo_verificacion="",
        fecha=pedido.fecha_creacion.date(),
        cliente_nombre=pedido.cliente.nombre_empresa,
        cliente_ruc=pedido.cliente.ruc,
        mostrar_ruc=True,
        cliente_direccion=pedido.cliente.direccion,
        cliente_telefono=pedido.cliente.telefono,
        cliente_correo=pedido.cliente.email_contacto,
        condicion_pago=Factura.CONDICION_CREDITO,
        notas=pedido.notas,
        subtotal=pedido.total_estimado,
        descuento_total=CERO,
        base_gravada=pedido.total_estimado,  # Simplificado
        base_exenta=CERO,
        itbms=CERO,  # Pedidos no tienen ITBMS todavía
        total=pedido.total_estimado,
        estado=Factura.ESTADO_EMITIDA,
    )

    # Crear líneas temporales
    lineas_temp = []
    for linea_pedido in pedido.lineas.all().select_related("producto"):
        producto = linea_pedido.producto
        # Determinar cobrar_por según si hay cajas
        cobrar_por = COBRAR_POR_CAJA if linea_pedido.cantidad_cajas > 0 else COBRAR_POR_UNIDAD

        linea_temp = LineaFactura(
            factura=factura_temp,
            orden=linea_pedido.orden,
            descripcion=producto.nombre,
            codigo_barras=producto.sku,
            categoria=producto.categoria.nombre if producto.categoria else "",
            cantidad=linea_pedido.cantidad_cajas
            if cobrar_por == COBRAR_POR_CAJA
            else linea_pedido.cantidad_unidades,
            precio_unitario=producto.precio_caja
            if cobrar_por == COBRAR_POR_CAJA
            else producto.precio_unidad,
            descuento_pct=CERO,
            gravada=producto.aplica_itbms,
            unidades_por_caja=producto.unidades_por_caja,
            cobrar_por=cobrar_por,
            monto=linea_pedido.subtotal,
            producto=producto,
        )
        lineas_temp.append(linea_temp)

    # Generar PDF
    from facturacion.models import ConfiguracionNegocio

    configuracion = ConfiguracionNegocio.cargar()
    contenido = generar_pdf(factura_temp, configuracion, lineas_temp)

    from django.http import HttpResponse

    respuesta = HttpResponse(contenido, content_type="application/pdf")
    respuesta[
        "Content-Disposition"
    ] = f'attachment; filename="PED-{pedido.pk:04d}.pdf"'
    return respuesta
