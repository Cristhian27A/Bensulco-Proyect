"""Generación del PDF de la factura con ReportLab.

El PDF se arma en memoria (BytesIO), no se guarda ningún archivo en disco.

Diseño: carta vertical, márgenes de 15 mm, tipografía Helvetica sin serifas
y un mínimo de 8 pt en todo el texto. Para que nada se monte ni se salga de
la página, el encabezado se dibuja a mano sobre el lienzo con coordenadas
exactas y el cuerpo (tabla de productos, totales y firmas) se arma con
Platypus dentro de marcos que ya dejan libre el espacio del encabezado.
"""

import io
import re
import unicodedata
from decimal import Decimal

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    KeepTogether,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

from facturacion.services.totales import (
    COBRAR_POR_CAJA,
    formato_precio,
    precio_efectivo,
)

ANCHO_PAGINA, ALTO_PAGINA = letter
MARGEN = 15 * mm
BORDE_IZQUIERDO = MARGEN
BORDE_DERECHO = ANCHO_PAGINA - MARGEN
ANCHO_UTIL = BORDE_DERECHO - BORDE_IZQUIERDO
TOPE_PAGINA = ALTO_PAGINA - MARGEN

# Altura reservada para el encabezado dibujado en el lienzo. Todo lo que
# queda entre este bloque y el pie es el espacio de la tabla de productos.
ALTO_ENCABEZADO = 150.0
TOPE_CUERPO_1 = TOPE_PAGINA - ALTO_ENCABEZADO      # 577.0
TOPE_CUERPO_N = ALTO_PAGINA - MARGEN - 30           # deja sitio al pie

COLOR_MARCA = "#3A0088"
# Color por defecto de la barra ORDEN DE COMPRA: version mas suave de la marca.
COLOR_BARRA = "#5B3A9E"
GRIS_OSCURO = colors.HexColor("#3C3C46")
GRIS_MEDIO = colors.HexColor("#6F6F7A")
GRIS_LINEA = colors.HexColor("#DCDCE4")
GRIS_SUAVE = colors.HexColor("#FAFAFC")
BLANCO = colors.white
NEGRO = colors.black

# Anchura de las columnas de la tabla de productos (sin columna de descuento).
COL_NUMERO = 28
COL_CANTIDAD = 60
COL_PRECIO = 78
COL_MONTO = 80

TAMANO_LOGO = 48
TAMANO_QR = 48

# Alto de la franja del titulo "ORDEN DE COMPRA" y separacion con lo de abajo.
ALTO_BARRA = 20
# Espacio que se deja entre el bloque "Facturado a" y el encabezado de la tabla.
ESPACIO_SOBRE_TABLA = 9


# --------------------------------------------------------------------------
# Colores
# --------------------------------------------------------------------------

def _componentes(color):
    """Devuelve (r, g, b) de 0 a 1 a partir de un objeto Color."""
    return color.red, color.green, color.blue


def _color_contraste(fondo):
    """Devuelve blanco o negro, el que se lea mejor sobre ``fondo``.

    Se usa la luminancia relativa perceived por el ojo, que pondera mas el
    verde que el azul. Asi una barra clara lleva texto negro y una oscura,
    texto blanco, sin que el cliente tenga que elegirlo a mano.
    """
    r, g, b = _componentes(fondo)

    def canal(valor):
        return valor / 12.92 if valor <= 0.03928 else ((valor + 0.055) / 1.055) ** 2.4

    luminancia = 0.2126 * canal(r) + 0.7152 * canal(g) + 0.0722 * canal(b)
    # Con contraste suficiente se usa blanco; si la barra es muy clara, negro.
    return NEGRO if luminancia > 0.45 else BLANCO


def _color_valido(valor, predeterminado):
    """Valida un color hexadecimal de la configuracion."""
    if not valor:
        valor = predeterminado
    valor = str(valor).strip()
    if not re.match(r"^#[0-9A-Fa-f]{6}$", valor):
        valor = predeterminado
    return valor


# --------------------------------------------------------------------------
# Estilos de texto
# --------------------------------------------------------------------------

def _estilos(color_marca, color_banda=None):
    morado = colors.HexColor(color_marca)
    texto_banda = color_banda if color_banda is not None else _color_contraste(morado)
    return {
        "empresa": ParagraphStyle(
            "empresa", fontName="Helvetica-Bold", fontSize=15, leading=17,
            textColor=colors.HexColor("#1A1A1F"),
        ),
        "empresa_detalle": ParagraphStyle(
            "empresa_detalle", fontName="Helvetica", fontSize=8, leading=9.2,
            textColor=GRIS_OSCURO,
        ),
        "facturado_a": ParagraphStyle(
            "facturado_a", fontName="Helvetica-Bold", fontSize=8.5, leading=10,
            textColor=GRIS_MEDIO,
        ),
        "cliente": ParagraphStyle(
            "cliente", fontName="Helvetica-Bold", fontSize=11.5, leading=13,
            textColor=colors.HexColor("#1A1A1F"),
        ),
        "cliente_detalle": ParagraphStyle(
            "cliente_detalle", fontName="Helvetica", fontSize=8, leading=9.6,
            textColor=GRIS_OSCURO,
        ),
        "serie": ParagraphStyle(
            "serie", fontName="Helvetica-Bold", fontSize=14.5, leading=16,
            textColor=morado, alignment=TA_RIGHT,
        ),
        "serie_detalle": ParagraphStyle(
            "serie_detalle", fontName="Helvetica", fontSize=8, leading=9,
            textColor=GRIS_OSCURO, alignment=TA_RIGHT,
        ),
        "qr_codigo": ParagraphStyle(
            "qr_codigo", fontName="Helvetica", fontSize=7.5, leading=9,
            textColor=GRIS_MEDIO, alignment=TA_RIGHT,
        ),
        "producto": ParagraphStyle(
            "producto", fontName="Helvetica-Bold", fontSize=8.5, leading=10,
            textColor=colors.HexColor("#1A1A1F"),
        ),
        "celda_numero": ParagraphStyle(
            "celda_numero", fontName="Helvetica", fontSize=8.5, leading=10,
            alignment=TA_LEFT,
        ),
        "celda_dinero": ParagraphStyle(
            "celda_dinero", fontName="Helvetica", fontSize=9, leading=10.6,
            alignment=TA_RIGHT,
        ),
        "celda_dinero_fuerte": ParagraphStyle(
            "celda_dinero_fuerte", fontName="Helvetica-Bold", fontSize=9, leading=10.6,
            alignment=TA_RIGHT,
        ),
        "encabezado_tabla": ParagraphStyle(
            "encabezado_tabla", fontName="Helvetica-Bold", fontSize=8.5, leading=10,
            textColor=BLANCO,
        ),
        "encabezado_tabla_dinero": ParagraphStyle(
            "encabezado_tabla_dinero", fontName="Helvetica-Bold", fontSize=8.5,
            leading=10, textColor=BLANCO, alignment=TA_RIGHT,
        ),
        "total_etiqueta": ParagraphStyle(
            "total_etiqueta", fontName="Helvetica", fontSize=8.5, leading=10.4,
            textColor=GRIS_OSCURO, alignment=TA_LEFT,
        ),
        "total_valor": ParagraphStyle(
            "total_valor", fontName="Helvetica", fontSize=9, leading=10.4,
            textColor=colors.HexColor("#1A1A1F"), alignment=TA_RIGHT,
        ),
        "total_banda": ParagraphStyle(
            "total_banda", fontName="Helvetica-Bold", fontSize=11, leading=13,
            textColor=texto_banda, alignment=TA_LEFT,
        ),
        "total_banda_valor": ParagraphStyle(
            "total_banda_valor", fontName="Helvetica-Bold", fontSize=11, leading=13,
            textColor=texto_banda, alignment=TA_RIGHT,
        ),
        "total_letras": ParagraphStyle(
            "total_letras", fontName="Helvetica-Oblique", fontSize=8, leading=9.8,
            textColor=GRIS_OSCURO, alignment=TA_RIGHT,
        ),
        "notas_titulo": ParagraphStyle(
            "notas_titulo", fontName="Helvetica-Bold", fontSize=9,
            leading=11, textColor=colors.HexColor("#1A1A1F"),
        ),
        "notas": ParagraphStyle(
            "notas", fontName="Helvetica", fontSize=8, leading=9.8,
            textColor=GRIS_OSCURO,
        ),
        "firma_nombre": ParagraphStyle(
            "firma_nombre", fontName="Helvetica-Bold", fontSize=8.5, leading=10.4,
            textColor=colors.HexColor("#1A1A1F"), alignment=TA_CENTER,
        ),
        "firma_texto": ParagraphStyle(
            "firma_texto", fontName="Helvetica", fontSize=8, leading=9.8,
            textColor=GRIS_MEDIO, alignment=TA_CENTER,
        ),
        "firma_cargo": ParagraphStyle(
            "firma_cargo", fontName="Helvetica", fontSize=7.5, leading=9.2,
            textColor=GRIS_MEDIO, alignment=TA_CENTER,
        ),
        "pie": ParagraphStyle(
            "pie", fontName="Helvetica", fontSize=8, leading=9.4,
            textColor=GRIS_MEDIO, alignment=TA_CENTER,
        ),
    }


# --------------------------------------------------------------------------
# Utilidades
# --------------------------------------------------------------------------

def _dinero(valor) -> str:
    """Formatea un monto con separador de miles y dos decimales."""
    if valor is None:
        valor = 0
    return f"{Decimal(valor):,.2f}"


def _escapar(texto) -> str:
    """Escapa el texto para usarlo dentro de un Paragraph."""
    texto = "" if texto is None else str(texto)
    texto = texto.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return texto


def _cantidad_con_unidades(linea) -> str:
    """"12.00 und" si se cobra por unidad, "1.00 caja" / "2.00 cajas" si por caja."""
    if linea.cobrar_por == COBRAR_POR_CAJA:
        palabra = "caja" if Decimal(linea.cantidad) == 1 else "cajas"
        return f"{_dinero(linea.cantidad)} {palabra}"
    return f"{_dinero(linea.cantidad)} und"


def _precio_para_mostrar(linea) -> str:
    """Precio efectivo con su unidad: "1.25 / und" o "30.00 / caja"."""
    precio = precio_efectivo(
        linea.precio_unitario, linea.unidades_por_caja, linea.cobrar_por
    )
    sufijo = " / caja" if linea.cobrar_por == COBRAR_POR_CAJA else " / und"
    return f"{formato_precio(precio)} {sufijo}".rstrip()


def _cortar_lineas(texto, ancho, fuente, tamano, maximo, sufijo="..."):
    """Parte un texto en varias lineas y limita cuantas se dibujan.

    El encabezado tiene un alto fijo, asi que un nombre muy largo no puede
    ocupar mas lineas de las previstas: se ajusta en varias lineas y, si
    aun asi no cabe, se termina en puntos suspensivos.
    """
    palabras = str(texto or "").split()
    if not palabras:
        return ""
    lineas = []
    actual = ""
    for palabra in palabras:
        prueba = f"{actual} {palabra}".strip()
        if not actual or stringWidth(prueba, fuente, tamano) <= ancho:
            actual = prueba
        else:
            lineas.append(actual)
            actual = palabra
    if actual:
        lineas.append(actual)
    if len(lineas) <= maximo:
        return "<br/>".join(_escapar(linea) for linea in lineas)

    # Sobra texto: se muestran las primeras lineas y se avisa con "...".
    lineas = lineas[:maximo]
    while lineas:
        candidato = f"{lineas[-1]} {sufijo}"
        if stringWidth(candidato, fuente, tamano) <= ancho:
            lineas[-1] = candidato
            break
        lineas.pop()
    return "<br/>".join(_escapar(linea) for linea in lineas)


def _color_hex(valor, predeterminado=COLOR_MARCA):
    """Valida el color de la configuración y devuelve un objeto Color."""
    if not valor:
        valor = predeterminado
    valor = str(valor).strip()
    if not re.match(r"^#[0-9A-Fa-f]{6}$", valor):
        valor = predeterminado
    return colors.HexColor(valor)


def nombre_archivo_pdf(factura) -> str:
    """FAC-2026-0001_ClienteSinTildes.pdf"""
    cliente = factura.cliente_nombre or "Cliente"
    cliente = unicodedata.normalize("NFKD", cliente)
    cliente = "".join(c for c in cliente if not unicodedata.combining(c))
    cliente = re.sub(r"[^A-Za-z0-9]+", "", cliente)
    cliente = cliente[:40] or "Cliente"
    return f"{factura.numero_serie}_{cliente}.pdf"


def texto_qr(factura) -> str:
    """Contenido del QR: texto legible, no una dirección web."""
    lineas = [
        f"FACTURA {factura.numero_serie}",
        f"Fecha: {factura.fecha.strftime('%d/%m/%Y')}",
        f"Cliente: {factura.cliente_nombre}",
        f"Total: B/. {_dinero(factura.total)}",
        f"Codigo: {factura.codigo_verificacion}",
    ]
    return "\n".join(lineas)


def _imagen_qr(texto: str, lado: int = TAMANO_QR):
    """Genera el QR con la librería qrcode y devuelve un ImageReader."""
    import qrcode
    from reportlab.lib.utils import ImageReader

    codigo = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=6,
        border=1,
    )
    codigo.add_data(texto)
    codigo.make(fit=True)
    imagen = codigo.make_image(fill_color="black", back_color="white")

    buffer = io.BytesIO()
    imagen.save(buffer, format="PNG")
    buffer.seek(0)
    return ImageReader(buffer), lado


def _imagen_logo(facturacion, lado: int = TAMANO_LOGO):
    """Devuelve el logo de la configuración como ImageReader, o None."""
    from reportlab.lib.utils import ImageReader

    if not facturacion or not facturacion.logo:
        return None
    try:
        facturacion.logo.open("rb")
        datos = facturacion.logo.read()
        facturacion.logo.close()
    except (OSError, ValueError):
        return None
    if not datos:
        return None

    import io as _io

    from PIL import Image

    try:
        with Image.open(_io.BytesIO(datos)) as abierta:
           dimensions = abierta.size
    except Exception:
        return None

    if not dimensions[0] or not dimensions[1]:
        return None

    return ImageReader(_io.BytesIO(datos))


# --------------------------------------------------------------------------
# Encabezado, dibujado a mano para que nada se desalinee
# --------------------------------------------------------------------------

def _dibujar_encabezado(lienzo, doc):
    factura = doc.factura
    configuracion = doc.configuracion
    morado = doc.morado
    estilos = doc.estilos

    lienzo.saveState()

    # --- logo cuadrado a la izquierda ---
    logo = doc.logo
    if logo is not None:
        try:
            ancho, alto = logo.getSize()
            escala = min(TAMANO_LOGO / ancho, TAMANO_LOGO / alto)
            ancho = ancho * escala
            alto = alto * escala
        except Exception:
            ancho = alto = TAMANO_LOGO
        lienzo.drawImage(
            logo,
            BORDE_IZQUIERDO,
            TOPE_PAGINA - TAMANO_LOGO,
            width=ancho,
            height=alto,
            preserveAspectRatio=True,
            anchor="n",
            mask="auto",
        )
    else:
        # Marco del logo para que el encabezado no se descomponga sin imagen.
        lienzo.setStrokeColor(GRIS_LINEA)
        lienzo.setLineWidth(0.8)
        lienzo.setFillColor(colors.HexColor("#F2F0F7"))
        lienzo.rect(
            BORDE_IZQUIERDO, TOPE_PAGINA - TAMANO_LOGO, TAMANO_LOGO, TAMANO_LOGO,
            stroke=1, fill=1,
        )
        lienzo.setFillColor(morado)
        lienzo.setFont("Helvetica-Bold", 15)
        lienzo.drawCentredString(
            BORDE_IZQUIERDO + TAMANO_LOGO / 2,
            TOPE_PAGINA - TAMANO_LOGO / 2 - 5,
            (configuracion.empresa_nombre or "?").strip()[:1].upper(),
        )

    # --- nombre de la empresa al lado del logo ---
    def columna(texto, estilo, x, y, ancho, alto_maximo=60, separacion=1):
        """Dibuja un Paragraph y devuelve el alto que ocupa."""
        parrafo = Paragraph(texto, estilo)
        parrafo.wrap(ancho, alto_maximo)
        parrafo.drawOn(lienzo, x, y - parrafo.height)
        return parrafo.height + separacion

    def columna_limitada(entradas, x, y, ancho, tope_inferior):
        """Dibuja lineas de arriba abajo mientras quede espacio hasta el tope.

        Si un nombre larguisimo deja sin sitio a los datos de mas abajo, se
        omiten en vez de invadir la tabla de productos.
        """
        for entrada in entradas:
            texto, estilo, fuente, tamano, lineas, separacion = entrada[:6]
            # La ultima bandera indica que el texto ya trae su formato.
            marcado = len(entrada) > 6 and entrada[6]
            if not texto:
                continue
            parrafo = Paragraph(
                texto if marcado
                else _cortar_lineas(texto, ancho, fuente, tamano, lineas),
                estilo,
            )
            parrafo.wrap(ancho, 200)
            if y - (parrafo.height + separacion) < tope_inferior:
                break
            parrafo.drawOn(lienzo, x, y - parrafo.height)
            y -= parrafo.height + separacion
        return y

    x_texto = BORDE_IZQUIERDO + TAMANO_LOGO + 14
    ancho_texto = ANCHO_UTIL - TAMANO_LOGO - 14 - (TAMANO_QR + 12)
    y = TOPE_PAGINA - columna(
        _cortar_lineas(configuracion.empresa_nombre, ancho_texto,
                       "Helvetica-Bold", 15, 2),
        estilos["empresa"], x_texto, TOPE_PAGINA, ancho_texto, separacion=2,
    )

    # La direccion ocupa su propia linea; el resto se junta para no
    # alargar el encabezado mas de lo necesario.
    if configuracion.empresa_direccion:
        y -= columna(
            _cortar_lineas(configuracion.empresa_direccion, ancho_texto,
                           "Helvetica", 8, 1),
            estilos["empresa_detalle"], x_texto, y, ancho_texto, alto_maximo=40,
        )
    contacto = "  ·  ".join([
        t for t in [
            configuracion.empresa_correo,
            configuracion.empresa_telefono,
            f"RUC: {configuracion.empresa_ruc}"
            if (configuracion.mostrar_ruc and configuracion.empresa_ruc) else "",
        ] if t
    ])
    if contacto:
        y -= columna(
            _escapar(contacto), estilos["empresa_detalle"],
            x_texto, y, ancho_texto, alto_maximo=40,
        )

    # --- QR en la esquina superior derecha ---
    qr, lado = doc.qr
    lienzo.drawImage(
        qr,
        BORDE_DERECHO - lado,
        TOPE_PAGINA - lado,
        width=lado,
        height=lado,
        preserveAspectRatio=True,
        mask="auto",
    )
    # Debajo del QR va solo el codigo de verificacion, en letra pequena: el
    # numero de serie ya aparece grande en la columna de la derecha.
    pie_qr = Paragraph(_escapar(factura.codigo_verificacion), estilos["qr_codigo"])
    ancho_pie, _alto_pie = pie_qr.wrap(lado + 40, 20)
    pie_qr.drawOn(
        lienzo,
        max(BORDE_IZQUIERDO, BORDE_DERECHO - ancho_pie),
        TOPE_PAGINA - lado - 15,
    )

    # --- barra con el título ---
    # Franja a todo lo ancho para que el nombre largo de la empresa nunca se
    # amontone con el titulo. Va en un color suave de la marca, no en negro,
    # y el texto es blanco o negro segun se lea mejor.
    y_barra = TOPE_PAGINA - 66 - ALTO_BARRA
    lienzo.setFillColor(doc.color_barra)
    lienzo.rect(BORDE_IZQUIERDO, y_barra, ANCHO_UTIL, ALTO_BARRA, stroke=0, fill=1)
    lienzo.setFillColor(doc.color_texto_barra)
    lienzo.setFont("Helvetica-Bold", 13)
    lienzo.drawCentredString(
        ANCHO_PAGINA / 2, y_barra + ALTO_BARRA / 2 - 4.5, "ORDEN DE COMPRA"
    )
    # Referencia para el resto del encabezado: todo lo de abajo arranca aqui.
    y_bajo_barra = y_barra - 8

    # --- columna izquierda: facturado a ---
    # Telefono y correo van juntos y, si el nombre es enorme, se omiten los
    # datos menos importantes: el encabezado nunca invade la tabla.
    contacto = "  ·  ".join(
        t for t in [factura.cliente_telefono, factura.cliente_correo] if t
    )
    datos_cliente = [
        factura.cliente_ruc if (factura.mostrar_ruc and factura.cliente_ruc) else "",
        factura.cliente_direccion,
        f"Comprar desde: {factura.sucursal}" if factura.sucursal else "",
        contacto,
    ]
    y = columna_limitada(
        [
            (f'<font size="8.5" color="#6F6F7A">Facturado a:</font>&nbsp; '
             f"{_cortar_lineas(factura.cliente_nombre, 214, 'Helvetica-Bold', 11.5, 2)}",
             estilos["cliente"], "Helvetica-Bold", 11.5, 2, 2, True),
        ] + [
            (texto, estilos["cliente_detalle"], "Helvetica", 8, 1, 0)
            for texto in datos_cliente
        ],
        BORDE_IZQUIERDO, y_bajo_barra, 300,
        # Se respeta el espacio pedido sobre el encabezado de la tabla.
        TOPE_CUERPO_1 + ESPACIO_SOBRE_TABLA,
    )

    # --- columna derecha: serie en morado y fecha ---
    x_derecha = BORDE_DERECHO - 200
    ancho_derecha = 200
    y_derecha = y_bajo_barra - columna(
        _escapar(factura.numero_serie), estilos["serie"],
        x_derecha, y_bajo_barra, ancho_derecha, alto_maximo=30,
        separacion=1,
    )

    detalles_derecha = [
        f"Fecha: {factura.fecha.strftime('%d/%m/%Y')}",
        f"Vence: {factura.fecha_vencimiento.strftime('%d/%m/%Y')}",
        f"Condición: {factura.texto_condicion_pago}",
    ]
    if factura.orden_compra:
        detalles_derecha.append(f"Orden de compra: {factura.orden_compra}")
    for texto in detalles_derecha:
        y_derecha -= columna(_escapar(texto), estilos["serie_detalle"],
                             x_derecha, y_derecha, ancho_derecha,
                             alto_maximo=30, separacion=0)

    lienzo.restoreState()


def _dibujar_marca_agua(lienzo, doc):
    """Marca de agua diagonal ANULADA, en todas las páginas."""
    if not getattr(doc, "factura", None) or not doc.factura.anulada:
        return
    lienzo.saveState()
    try:
        lienzo.setFillAlpha(0.12)
    except Exception:
        pass
    lienzo.translate(ANCHO_PAGINA / 2, ALTO_PAGINA / 2)
    lienzo.rotate(38)
    lienzo.setFillColor(colors.HexColor("#B3261E"))
    lienzo.setFont("Helvetica-Bold", 62)
    lienzo.drawCentredString(0, -20, "ANULADA")
    lienzo.restoreState()


def _dibujar_pie(lienzo, doc, total_paginas):
    """Pie de página: empresa, serie y "Página X de Y"."""
    factura = doc.factura
    configuracion = doc.configuracion
    partes = [configuracion.empresa_nombre]
    if configuracion.mostrar_ruc and configuracion.empresa_ruc:
        partes.append(f"RUC: {configuracion.empresa_ruc}")
    partes.extend(
        [f"Factura {factura.numero_serie}",
         f"Página {lienzo.getPageNumber()} de {total_paginas}"]
    )
    texto = "  ·  ".join(partes)
    styles = doc.estilos
    parrafo = Paragraph(_escapar(texto), styles["pie"])
    parrafo.wrap(ANCHO_UTIL, 20)
    parrafo.drawOn(lienzo, BORDE_IZQUIERDO, 26)


class LienzoNumerado(canvas.Canvas):
    """Lienzo que dibuja el pie al final, cuando ya se sabe cuántas páginas hay.

    Guarda el estado de cada página y al final vuelve a pasarlas una por una
    para escribir "Página X de Y" en todas.
    """

    # El documento se asigna desde generar_pdf, porque el lienzo no lo recibe.
    documento = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._paginas = []

    def showPage(self):
        self._paginas.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        total = len(self._paginas)
        for estado in self._paginas:
            self.__dict__.update(estado)
            _dibujar_pie(self, self.documento, total)
            super().showPage()
        super().save()


# --------------------------------------------------------------------------
# Cuerpo de la factura
# --------------------------------------------------------------------------

def _celda_producto(linea, estilos):
    """Nombre del producto en negrita y, debajo, código, categoría y la
    referencia de la caja en gris."""
    texto = f"<b>{_escapar(linea.descripcion)}</b>"
    detalles = []
    if linea.codigo_barras:
        detalles.append(f"Código: {_escapar(linea.codigo_barras)}")
    if linea.categoria:
        detalles.append(_escapar(linea.categoria))
    if linea.unidades_por_caja > 1:
        detalles.append(f"Caja de {linea.unidades_por_caja} und")
    if detalles:
        # El mínimo de 8 pt se respeta también en esta línea de detalle.
        texto += '<br/><font size="8" color="#6F6F7A">' + "  ·  ".join(detalles) + "</font>"
    return Paragraph(texto, estilos["producto"])


def _tabla_productos(factura, estilos, morado):
    encabezados = [
        Paragraph("N.º", estilos["encabezado_tabla"]),
        Paragraph("Producto", estilos["encabezado_tabla"]),
        Paragraph("Cant.", estilos["encabezado_tabla_dinero"]),
        Paragraph("Precio unit.", estilos["encabezado_tabla_dinero"]),
        Paragraph("Monto", estilos["encabezado_tabla_dinero"]),
    ]
    filas = [encabezados]
    for linea in factura.lineas.all():
        filas.append([
            Paragraph(str(linea.orden), estilos["celda_numero"]),
            _celda_producto(linea, estilos),
            Paragraph(_cantidad_con_unidades(linea), estilos["celda_dinero"]),
            Paragraph(_precio_para_mostrar(linea), estilos["celda_dinero"]),
            Paragraph(_dinero(linea.monto), estilos["celda_dinero_fuerte"]),
        ])

    # Sin columna de descuento: el producto se lleva lo que sobra del ancho.
    col_producto = ANCHO_UTIL - (COL_NUMERO + COL_CANTIDAD + COL_PRECIO + COL_MONTO)

    tabla = Table(
        filas,
        colWidths=[COL_NUMERO, col_producto, COL_CANTIDAD, COL_PRECIO, COL_MONTO],
        repeatRows=1,
    )
    estilo_tabla = [
        ("BACKGROUND", (0, 0), (-1, 0), morado),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ALIGN", (2, 0), (-1, -1), "RIGHT"),
        ("ALIGN", (0, 0), (0, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, 0), 4),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 4),
        ("TOPPADDING", (0, 1), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("LINEBELOW", (0, 1), (-1, -1), 0.4, GRIS_LINEA),
        ("LINEBELOW", (0, 0), (-1, 0), 0.6, morado),
        ("BOX", (0, 0), (-1, -1), 0.4, GRIS_LINEA),
    ]
    for indice in range(1, len(filas)):
        if indice % 2 == 0:
            estilo_tabla.append(("BACKGROUND", (0, indice), (-1, indice), GRIS_SUAVE))
    tabla.setStyle(TableStyle(estilo_tabla))
    return tabla


def _cuadro_totales(factura, estilos, morado):
    """Solo tres filas: subtotal, ITBMS y gran total.

    Los desgloses (base gravada, base exenta, portes y descuentos) se quitaron
    por peticion del cliente. El ITBMS sigue siendo solo sobre las lineas
    gravadas, asi que subtotal + ITBMS sigue dando el gran total.
    """
    filas = [
        ("Subtotal", factura.subtotal),
        ("ITBMS 7%", factura.itbms),
    ]
    ancho_etiqueta = 108
    ancho_valor = ANCHO_UTIL - 300 - 8 - ancho_etiqueta
    datos = []
    for etiqueta, valor in filas:
        datos.append([
            Paragraph(etiqueta, estilos["total_etiqueta"]),
            Paragraph(_dinero(valor), estilos["total_valor"]),
        ])

    datos.append([
        Paragraph("Gran total", estilos["total_banda"]),
        Paragraph(f"B/. {_dinero(factura.total)}", estilos["total_banda_valor"]),
    ])

    tabla = Table(
        datos,
        colWidths=[ancho_etiqueta, ancho_valor],
        rowHeights=[16] * len(filas) + [20],
    )
    estilo_tabla = [
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -2), 2),
        ("LINEBELOW", (0, 0), (-1, -2), 0.5, morado),
        ("BACKGROUND", (0, -1), (-1, -1), morado),
        ("TOPPADDING", (0, -1), (-1, -1), 4),
        ("BOTTOMPADDING", (0, -1), (-1, -1), 4),
        ("BOX", (0, 0), (-1, -1), 0.5, GRIS_LINEA),
    ]
    tabla.setStyle(TableStyle(estilo_tabla))
    return tabla


def _bloque_notas(factura, estilos, morado, ancho):
    """Lista de flowables: línea morada, título "Notas" y el texto.

    Se devuelve como lista (no como KeepTogether) porque va dentro de una
    celda de tabla, y ahí ReportLab no puede medir un bloque agrupado.
    Sin notas, el bloque no se imprime.
    """
    if not (factura.notas or "").strip():
        return Spacer(1, 1)
    linea = Table(
        [[""]],
        colWidths=[ancho],
        rowHeights=[2.5],
    )
    linea.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), morado),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    titulo = Paragraph("Notas", estilos["notas_titulo"])
    texto = Paragraph(
        _escapar(factura.notas.strip()).replace("\n", "<br/>"),
        estilos["notas"],
    )
    return [linea, Spacer(1, 5), titulo, Spacer(1, 3), texto]


def _bloque_firmas(factura, estilos):
    """Las dos lineas de firma, a la misma altura.

    Ambas columnas arrancan con el mismo espacio y la misma linea, asi que
    "Firma" y "Recibido por" quedan en la misma linea. El nombre del vendedor
    y "(Vendedor)" van debajo, solo en la columna izquierda.
    """
    def columna(cargo, nombre=None):
        partes = [
            Spacer(1, 22),
            Paragraph("_" * 34, estilos["firma_texto"]),
            Spacer(1, 2),
            Paragraph(cargo, estilos["firma_texto"]),
        ]
        if nombre:
            partes.append(Spacer(1, 3))
            partes.append(Paragraph(_escapar(nombre), estilos["firma_nombre"]))
            partes.append(Paragraph("(Vendedor)", estilos["firma_cargo"]))
        return partes

    contenido = [
        columna("Firma", (factura.vendedor or "").strip()),
        columna("Recibido por"),
    ]
    tabla = Table(
        [contenido],
        colWidths=[ANCHO_UTIL / 2 - 10, ANCHO_UTIL / 2 - 10],
    )
    tabla.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    return tabla


def _cuerpo_final(factura, estilos, morado):
    """Totales, notas y firmas. Siempre viajan juntos en la última página."""
    ancho_izquierda = 300
    ancho_derecha = ANCHO_UTIL - ancho_izquierda - 12

    izquierda = _bloque_notas(factura, estilos, morado, ancho_izquierda)
    derecha = _cuadro_totales(factura, estilos, morado)

    dos_columnas = Table(
        [[izquierda, derecha]],
        colWidths=[ancho_izquierda, ancho_derecha + 12],
    )
    dos_columnas.setStyle(TableStyle([
        ("VALIGN", (0, 0), (0, 0), "TOP"),
        ("VALIGN", (1, 0), (1, 0), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))

    partes = [dos_columnas, Spacer(1, 5)]
    partes.append(Paragraph(_escapar(factura.total_en_letras), estilos["total_letras"]))
    partes.append(Spacer(1, 14))
    partes.append(_bloque_firmas(factura, estilos))

    return partes


# --------------------------------------------------------------------------
# Documento
# --------------------------------------------------------------------------

class PlantillaFactura(BaseDocTemplate):
    """Documento con un marco más corto en la primera página (por el encabezado)."""

    def __init__(self, buffer_destino, factura, configuracion, **kwargs):
        super().__init__(
            buffer_destino,
            pagesize=letter,
            leftMargin=MARGEN,
            rightMargin=MARGEN,
            topMargin=MARGEN,
            bottomMargin=MARGEN,
            title=f"Factura {factura.numero_serie}",
            author=configuracion.empresa_nombre,
            subject=f"Factura {factura.numero_serie} - {factura.cliente_nombre}",
            **kwargs,
        )
        # Tres colores independientes, todos configurables: la barra del
        # titulo, la tabla de productos y la banda del gran total.
        self.color_principal = _color_valido(
            getattr(configuracion, "color_principal", ""), COLOR_MARCA
        )
        self.color_tabla = _color_hex(
            _color_valido(getattr(configuracion, "color_tabla", ""), COLOR_MARCA)
        )
        self.color_barra = _color_hex(
            _color_valido(
                getattr(configuracion, "color_barra_factura", ""), COLOR_BARRA
            )
        )
        # El texto de la barra y de la banda cambia segun el contraste.
        self.color_texto_barra = _color_contraste(self.color_barra)
        self.color_texto_banda = _color_contraste(self.color_tabla)

        # "morado" es el color de la tabla; los estilos reciben el color de
        # texto que contrasta con el, para la banda del gran total.
        self.morado = self.color_tabla
        self.estilos = _estilos(self.color_principal, self.color_texto_banda)
        self.factura = factura
        self.configuracion = configuracion
        self.qr = _imagen_qr(texto_qr(factura))
        self.logo = _imagen_logo(configuracion)

        marco_primera = Frame(
            BORDE_IZQUIERDO, MARGEN, ANCHO_UTIL,
            TOPE_CUERPO_1 - MARGEN, id="cuerpo-primera",
            leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0,
        )
        marco_siguiente = Frame(
            BORDE_IZQUIERDO, MARGEN, ANCHO_UTIL,
            TOPE_CUERPO_N - MARGEN, id="cuerpo-siguiente",
            leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0,
        )

        self.addPageTemplates([
            PageTemplate(
                id="primera",
                frames=[marco_primera],
                onPage=self._al_dibujar_primera,
            ),
            PageTemplate(
                id="siguiente",
                frames=[marco_siguiente],
                onPage=self._al_dibujar_siguiente,
            ),
        ])

    def _al_dibujar_primera(self, lienzo, doc):
        _dibujar_marca_agua(lienzo, doc)
        _dibujar_encabezado(lienzo, doc)

    def _al_dibujar_siguiente(self, lienzo, doc):
        _dibujar_marca_agua(lienzo, doc)


def generar_pdf(factura, configuracion=None) -> bytes:
    """Devuelve los bytes del PDF de la factura."""
    if configuracion is None:
        from facturacion.models import ConfiguracionNegocio

        configuracion = ConfiguracionNegocio.cargar()

    buffer = io.BytesIO()
    documento = PlantillaFactura(buffer, factura, configuracion)

    historia = [
        NextPageTemplate("siguiente"),
        _tabla_productos(factura, documento.estilos, documento.morado),
    ]
    # El bloque final va entero en una sola pagina: si no cabe en la que
    # termino la tabla, pasa completa a la siguiente.
    historia.append(
        KeepTogether(_cuerpo_final(factura, documento.estilos, documento.morado))
    )

    def nuevo_lienzo(*args, **kwargs):
        lienzo = LienzoNumerado(*args, **kwargs)
        lienzo.documento = documento
        return lienzo

    documento.build(historia, canvasmaker=nuevo_lienzo)
    return buffer.getvalue()
