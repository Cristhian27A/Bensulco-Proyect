"""Pruebas de la generación del PDF."""

import io
from datetime import date
from decimal import Decimal

from django.test import TestCase
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter

from facturacion.models import COBRAR_POR_CAJA, ConfiguracionNegocio, Factura
from facturacion.services import pdf as servicio_pdf
from facturacion.services.pdf import generar_pdf, nombre_archivo_pdf, texto_qr
from facturacion.services.serie import anular_factura, crear_factura
from facturacion.tests import utiles_pdf

D = Decimal


def linea(descripcion, cantidad="1", precio="10.00", codigo="", categoria="",
          gravada=True, unidades_por_caja=1, cobrar_por="unidad"):
    return {
        "descripcion": descripcion,
        "codigo_barras": codigo,
        "categoria": categoria,
        "cantidad": D(cantidad),
        "precio_unitario": D(precio),
        "gravada": gravada,
        "unidades_por_caja": unidades_por_caja,
        "cobrar_por": cobrar_por,
    }


# Nombre de producto realista: cabe en una linea, como los de una tienda.
PRODUCTOS = [
    "Aceite vegetal 900 ml", "Arroz precocido 5 lb", "Azúcar refinada 2 kg",
    "Leche entera 1 L", "Pan dulce", "Jabón de ropa 3 L",
    "Cloro desinfectante 2 L", "Detergente en polvo 5 kg",
    "Papel higiénico 12 rollos", "Galletas de soda", "Café molido 500 g",
    "Sal de mesa 1 kg", "Vinagre blanco 1 L", "Mayonesa 500 g",
    "Harina de trigo 4 lb", "Aceite de oliva 500 ml", "Pasta corta 1 lb",
    "Café instantáneo 100 g", "Té negro 20 sobre", "Miel de abeja 250 g",
    "Mantequilla 250 g", "Queso blanco 500 g", "Jamón cocido 250 g",
    "Sardinas en lata", "Atún en aceite 185 g", "Maíz dulce 340 g",
    "Frijoles negros 1 lb", "Lentejas 1 lb", "Avena en hojuelas 1 lb",
    "Galón de agua 5 L", "Bebida gaseosa 2 L", "Jugo de naranja 1 L",
    "Cerveza 330 ml", "Vino tinto 750 ml", "Refresco de cola 2 L",
    "Papel toalla", "Lavavajillas 500 ml", "Suavizante 1 L",
    "Fósforo caja 12", "Pilas AA 4", "Bombillo LED 9 W",
    "Guantes de nitrilo 100", "Mascarilla 50",
]


def configuracion_con(**colores):
    """Configuracion con los colores que se le pasen."""
    configuracion = ConfiguracionNegocio.cargar()
    for campo, valor in colores.items():
        setattr(configuracion, campo, valor)
    return configuracion


def factura_con(cantidad_lineas, **extra):
    """Factura de ejemplo, con nombres de producto de una tienda."""
    datos = {
        "fecha": date(2026, 9, 29),
        "cliente_nombre": "CLIENTE DE PRUEBA S.A.",
        "cliente_ruc": "1-2345678-90-123",
        "cliente_direccion": "Avenida Central, Ciudad de Panamá",
        "cliente_telefono": "+507 0000-0000",
        "cliente_correo": "compras@cliente.com",
        "sucursal": "Sucursal Centro",
        "vendedor": "María Pérez",
        "condicion_pago": "credito",
        "notas": "Pago a 30 días. Entrega en el local del cliente.",
    }
    datos.update(extra)
    lineas = [
        linea(
            PRODUCTOS[(i - 1) % len(PRODUCTOS)],
            cantidad=str(i % 4 + 1),
            precio=f"{10 + i}.{i}0",
            codigo=f"75012345678{i:02d}",
            categoria="Alimentos",
        )
        for i in range(1, cantidad_lineas + 1)
    ]
    return crear_factura(datos, lineas)


class PruebaPDFValido(TestCase):
    """Factura de 12 productos: debe caber en una sola hoja de carta."""

    @classmethod
    def setUpTestData(cls):
        cls.factura = factura_con(12)
        cls.configuracion = ConfiguracionNegocio.cargar()
        cls.contenido = generar_pdf(cls.factura, cls.configuracion)

    def test_devuelve_un_pdf_valido(self):
        self.assertTrue(self.contenido.startswith(b"%PDF-"))
        self.assertGreater(len(self.contenido), 3000)
        self.assertIn(b"%%EOF", self.contenido[-2048:])

    def test_doce_productos_caben_en_una_sola_hoja(self):
        self.assertEqual(utiles_pdf.numero_de_paginas(self.contenido), 1)

    def test_el_tamano_es_carta_vertical(self):
        self.assertEqual(letter, (612.0, 792.0))
        cajas = utiles_pdf.cajas(
            utiles_pdf.texto_normal(utiles_pdf.fragmentos_de_pagina(self.contenido, 0))
        )
        # Si el MediaBox fuera carta, el ancho máximo del texto no lo supera.
        for caja in cajas:
            self.assertLessEqual(caja[2], letter[0], caja[4])

    def test_el_pdf_tiene_una_sola_pagina_declarada(self):
        self.assertIn(b"/Type /Pages", self.contenido)
        self.assertIn(b"/Type /Page", self.contenido)

    def test_los_doce_productos_aparecen_en_el_pdf(self):
        texto = utiles_pdf.texto_de_pagina(self.contenido, 0)
        for linea in self.factura.lineas.all():
            self.assertIn(linea.descripcion, texto)
            self.assertIn(linea.codigo_barras, texto)
        self.assertEqual(self.factura.lineas.count(), 12)

    def test_aparecen_el_titulo_la_serie_y_los_totales(self):
        texto = utiles_pdf.texto_de_pagina(self.contenido, 0)
        self.assertIn("ORDEN DE COMPRA", texto)
        self.assertIn(self.factura.numero_serie, texto)
        self.assertIn("Gran total", texto)
        self.assertIn("ITBMS 7%", texto)
        self.assertIn("Facturado a:", texto)
        self.assertIn("Notas", texto)
        self.assertIn("Firma", texto)
        self.assertIn("Recibido por", texto)
        self.assertIn("Página 1 de 1", texto)


class PruebaPDFMultipagina(TestCase):
    """Factura de 40 productos: varias páginas y el bloque final entero al final."""

    @classmethod
    def setUpTestData(cls):
        cls.factura = factura_con(40)
        cls.configuracion = ConfiguracionNegocio.cargar()
        cls.contenido = generar_pdf(cls.factura, cls.configuracion)
        cls.paginas = utiles_pdf.textos_por_pagina(cls.contenido)

    def test_tiene_varias_paginas(self):
        self.assertGreater(utiles_pdf.numero_de_paginas(self.contenido), 1)

    def test_el_bloque_de_totales_aparece_solo_en_la_ultima_pagina(self):
        for indice, texto in enumerate(self.paginas[:-1]):
            self.assertNotIn("Gran total", texto, f"En la página {indice + 1}")
            self.assertNotIn("ITBMS 7%", texto, f"En la página {indice + 1}")
        self.assertIn("Gran total", self.paginas[-1])

    def test_las_firmas_aparecen_solo_en_la_ultima_pagina(self):
        for indice, texto in enumerate(self.paginas[:-1]):
            self.assertNotIn("Recibido por", texto, f"En la página {indice + 1}")
            self.assertNotIn("Firma", texto, f"En la página {indice + 1}")
        self.assertIn("Firma", self.paginas[-1])
        self.assertIn("Recibido por", self.paginas[-1])

    def test_el_total_en_letras_aparece_solo_en_la_ultima_pagina(self):
        from facturacion.services.numero_a_letras import total_en_letras

        letras = total_en_letras(self.factura.total)
        self.assertIn("CON", letras)
        for indice, texto in enumerate(self.paginas[:-1]):
            self.assertNotIn(f"{self.factura.total:,.2f} D", texto)
        self.assertIn("DÓLARES", self.paginas[-1])

    def test_las_notas_solo_al_final(self):
        for indice, texto in enumerate(self.paginas[:-1]):
            self.assertNotIn("Pago a 30", texto, f"En la página {indice + 1}")
        self.assertIn("Pago a 30", self.paginas[-1])

    def test_los_cuarenta_productos_se_imprimen_por_pagina(self):
        # Todas las páginas con productos repiten el encabezado de la tabla.
        for indice, texto in enumerate(self.paginas[:-1]):
            self.assertIn("Producto", texto, f"En la página {indice + 1}")
        # Los 40 productos salen, con su codigo de barras, entre todas.
        self.assertGreaterEqual(
            sum(texto.count("75012345678") for texto in self.paginas), 40
        )
        # Y la última página es la que cierra con totales y firmas.
        self.assertIn("Gran total", self.paginas[-1])

    def test_el_encabezado_repetido_no_trae_la_columna_de_descuento(self):
        for indice, texto in enumerate(self.paginas[:-1]):
            self.assertIn("Precio unit.", texto, f"En la página {indice + 1}")
            self.assertNotIn("Desc.", texto, f"En la página {indice + 1}")
            self.assertNotIn("Descuento", texto, f"En la página {indice + 1}")

    def test_ninguna_de_las_cuarenta_lineas_lleva_descuento(self):
        self.assertEqual(self.factura.lineas.count(), 40)
        for linea in self.factura.lineas.all():
            self.assertEqual(linea.descuento_pct, D("0.00"))
            self.assertEqual(
                linea.monto,
                (linea.cantidad * linea.precio_unitario).quantize(D("0.01")),
            )

    def test_no_hay_solapes_en_ninguna_de_las_paginas(self):
        for indice in range(len(self.paginas)):
            solapes = utiles_pdf.solapamientos(self.contenido, indice)
            self.assertEqual(
                solapes, [],
                f"Solapes en la página {indice + 1}: "
                f"{[(a[4], b[4]) for a, b in solapes]}",
            )

    def test_el_bloque_final_cabe_entero_en_la_ultima_pagina(self):
        """El bloque completo, sin cortes, tiene que caber en una página."""
        # Si el bloque se partiera entre dos páginas, sus textos quedarian
        # separados: el ultimo elemento (firmas) cae en la ultima pagina y
        # el primero (notas) en la misma, sin huecos intermedios.
        ultima = self.paginas[-1]
        from facturacion.services.numero_a_letras import total_en_letras

        for texto in [
            "Gran total", total_en_letras(self.factura.total),
            "Recibido por", "Firma",
        ]:
            self.assertIn(texto, ultima)
        # El pie de pagina va aparte: se mide solo el bloque del cuerpo.
        cajas = [
            c for c in utiles_pdf.cajas(
                utiles_pdf.texto_normal(
                    utiles_pdf.fragmentos_de_pagina(
                        self.contenido, len(self.paginas) - 1
                    )
                )
            )
            if c[3] > 45
        ]
        arriba = max(c[3] for c in cajas)
        abajo = min(c[1] for c in cajas)
        self.assertLessEqual(
            arriba - abajo, servicio_pdf.TOPE_CUERPO_N - servicio_pdf.MARGEN,
            f"El bloque final mide {arriba - abajo:.1f} y una pagina del cuerpo "
            f"ofrece {servicio_pdf.TOPE_CUERPO_N - servicio_pdf.MARGEN:.1f}",
        )

    def test_cada_pagina_recibe_el_pie_con_su_numero(self):
        total = len(self.paginas)
        for indice in range(total):
            self.assertIn(
                f"Página {indice + 1} de {total}", self.paginas[indice]
            )

    def test_el_encabezado_completo_solo_va_en_la_primera_pagina(self):
        self.assertIn("ORDEN DE COMPRA", self.paginas[0])
        for texto in self.paginas[1:]:
            self.assertNotIn("Facturado a:", texto)


class PruebaMargenesYSolapes(TestCase):
    """Ningún texto puede salirse de los márgenes ni montarse con otro."""

    def _revisar(self, factura):
        contenido = generar_pdf(factura, ConfiguracionNegocio.cargar())
        paginas = utiles_pdf.textos_por_pagina(contenido)
        for indice, _texto in enumerate(paginas):
            cajas = utiles_pdf.cajas(
                utiles_pdf.texto_normal(utiles_pdf.fragmentos_de_pagina(contenido, indice))
            )
            self.assertTrue(cajas, "La página no tiene texto")
            for caja in cajas:
                # Márgenes de 15 mm = 42.5 puntos, con tolerancia mínima.
                self.assertGreaterEqual(
                    caja[0], servicio_pdf.MARGEN - 1.5,
                    f"Se sale por la izquierda: {caja[4]!r}",
                )
                self.assertLessEqual(
                    caja[2], servicio_pdf.ANCHO_PAGINA - servicio_pdf.MARGEN + 1.5,
                    f"Se sale por la derecha: {caja[4]!r}",
                )
                self.assertGreaterEqual(
                    caja[1], 20,
                    f"Se sale por abajo: {caja[4]!r}",
                )
                self.assertLessEqual(
                    caja[3], servicio_pdf.ANCHO_PAGINA * 0 + 792,
                    f"Se sale por arriba: {caja[4]!r}",
                )
            solapes = utiles_pdf.solapamientos(contenido, indice)
            self.assertEqual(
                solapes, [],
                f"Textos superpuestos en la página {indice + 1}: "
                + "; ".join(f"{a[4]!r} / {b[4]!r}" for a, b in solapes[:5]),
            )
        return contenido

    def test_factura_de_12_productos_sin_solapes(self):
        self._revisar(factura_con(12))

    def test_factura_de_40_productos_sin_solapes(self):
        self._revisar(factura_con(40))

    def test_texto_muy_largo_sin_solapes(self):
        factura = factura_con(
            6,
            cliente_nombre=(
                "EMPRESA COMERCIAL DE DISTRIBUCION Y SERVICIOS INTEGRALES "
                "SOCIEDAD ANONIMA DE PANAMA (EJEMPLO) CON UN NOMBRE "
                "EXTREMADAMENTE LARGO PARA PROBAR EL AJUSTE DE TEXTO"
            ),
        )
        self._revisar(factura)

    def test_factura_anulada_sin_solapes(self):
        factura = factura_con(8)
        anular_factura(factura)
        factura.refresh_from_db()
        self._revisar(factura)

    def test_factura_sin_notas_ni_vendedor_sin_solapes(self):
        self._revisar(factura_con(5, notas="", vendedor=""))

    def test_factura_sin_ruc_del_cliente_sin_solapes(self):
        self._revisar(factura_con(6, cliente_ruc="", mostrar_ruc=False))


class PruebaEncabezadoNoSeMontaConElCuerpo(TestCase):
    """El encabezado dibujado a mano debe quedar por encima del marco del cuerpo."""

    def test_el_encabezado_no_baja_del_tope_del_cuerpo(self):
        """El texto del encabezado debe quedar por encima de la tabla."""
        contenido = generar_pdf(factura_con(4), ConfiguracionNegocio.cargar())
        cajas = utiles_pdf.cajas(
            utiles_pdf.texto_normal(utiles_pdf.fragmentos_de_pagina(contenido, 0))
        )
        # Lo que se dibuja a mano (encabezado) frente a lo que arma Platypus
        # (tabla de productos). Se separan por la linea negra del encabezado.
        encabezado = [c for c in cajas if c[4] in {
            "ORDEN DE COMPRA", "Facturado a:", "CLIENTE DE PRUEBA S.A.",
        }]
        tabla = [c for c in cajas if c[4] in {"Producto", "N.\u00ba"}]
        self.assertTrue(encabezado, "No se encontro el encabezado")
        self.assertTrue(tabla, "No se encontro la tabla de productos")
        self.assertGreaterEqual(
            min(c[1] for c in encabezado), max(c[3] for c in tabla) - 1.0,
            "El encabezado se monta con la tabla de productos",
        )
        # Y ningun texto del encabezado baja del marco donde arranca el cuerpo.
        a_mano = {
            "ORDEN DE COMPRA", "Facturado a:", "CLIENTE DE PRUEBA S.A.",
            "MI EMPRESA S.A. (EJEMPLO)",
            "1-2345678-90-123", "Avenida Central, Ciudad de Panam\u00e1",
            "Comprar desde: Sucursal Centro",
            "+507 0000-0000 \u00b7 compras@cliente.com",
            "Fecha: 29/09/2026",
            "Condici\u00f3n: Cr\u00e9dito",
        }
        dibujados = [c for c in cajas if c[4] in a_mano]
        self.assertTrue(dibujados, "No se encontro el texto del encabezado")
        self.assertGreaterEqual(
            min(c[1] for c in dibujados), servicio_pdf.TOPE_CUERPO_1 - 1.5,
            f"El encabezado baja a {min(c[1] for c in dibujados):.1f} y el cuerpo "
            f"empieza en {servicio_pdf.TOPE_CUERPO_1:.1f}",
        )

    def test_el_pie_queda_dentro_del_margen_inferior(self):
        factura = factura_con(2)
        estilos = servicio_pdf._estilos(ConfiguracionNegocio.cargar().color_principal)
        parrafo = None
        from reportlab.platypus import Paragraph

        parrafo = Paragraph("Empresa · Factura FAC-2026-0001 · Página 1 de 1", estilos["pie"])
        _, alto = parrafo.wrap(servicio_pdf.ANCHO_UTIL, 20)
        # El pie se dibuja en y=26, o sea por debajo del marco (42.5).
        self.assertLess(26 + alto, servicio_pdf.MARGEN)
        self.assertGreater(26, 0)


class _Memoria:
    """Archivo en memoria mínimo para construir el documento."""

    def __init__(self):
        self.datos = bytearray()

    def write(self, texto):
        self.datos.extend(texto)
        return len(texto)

    def tell(self):
        return len(self.datos)


class _LienzoFalso:
    """Lienzo que registra las coordenadas y no dibuja nada."""

    def __init__(self):
        self.minimo = 10 ** 6
        self.setas = {}

    def saveState(self):
        pass

    def restoreState(self):
        pass

    def setStrokeColor(self, *args):
        pass

    def setLineWidth(self, *args):
        pass

    def setFillColor(self, *args):
        pass

    def setFont(self, *args):
        pass

    def line(self, *args):
        pass

    def rect(self, *args, **kwargs):
        pass

    def drawImage(self, *args, **kwargs):
        pass

    def translate(self, *args):
        pass

    def rotate(self, *args):
        pass

    def setFillAlpha(self, *args):
        pass

    def drawString(self, x, y, texto, *args, **kwargs):
        self.minimo = min(self.minimo, y)

    def drawCentredString(self, x, y, texto, *args, **kwargs):
        self.minimo = min(self.minimo, y)


class PruebaMarcaDeAgua(TestCase):
    def test_factura_anulada_lleva_la_marca_agua(self):
        factura = factura_con(3)
        anular_factura(factura)
        factura.refresh_from_db()
        self.assertTrue(factura.anulada)
        contenido = generar_pdf(factura, ConfiguracionNegocio.cargar())
        # La marca se dibuja como texto huge, puede venir troceada; se
        # comprueba el texto visible de la última página.
        textos = " ".join(utiles_pdf.textos_por_pagina(contenido))
        self.assertIn("ANULADA", textos)

    def test_factura_emitida_no_lleva_la_marca_agua(self):
        factura = factura_con(3)
        contenido = generar_pdf(factura, ConfiguracionNegocio.cargar())
        textos = " ".join(utiles_pdf.textos_por_pagina(contenido))
        self.assertNotIn("ANULADA", textos)


class PruebaNombreDeArchivo(TestCase):
    def test_quita_tildes_espacios_y_caracteres_especiales(self):
        factura = factura_con(1, cliente_nombre="Ñandú Cía. S.A. (Panamá) - ¡Oferta! #1")
        nombre = nombre_archivo_pdf(factura)
        self.assertEqual(nombre, "FAC-2026-0001_NanduCiaSAPanamaOferta1.pdf")
        self.assertNotRegex(nombre, r"[áéíóúñüÁÉÍÓÚÑÜ\s()!#]")

    def test_nombre_sin_tildes_se_conserva(self):
        factura = factura_con(1, cliente_nombre="Distribuidora Bensulco")
        self.assertEqual(
            nombre_archivo_pdf(factura), "FAC-2026-0001_DistribuidoraBensulco.pdf"
        )

    def test_nombre_largo_se_recorta(self):
        factura = factura_con(1, cliente_nombre="X" * 200)
        self.assertLessEqual(len(nombre_archivo_pdf(factura)), 60)


class PruebaQRYTexto(TestCase):
    def test_el_qr_no_depende_de_un_sitio_publico(self):
        factura = factura_con(2)
        contenido_qr = texto_qr(factura)
        self.assertIn(factura.numero_serie, contenido_qr)
        self.assertIn(factura.cliente_nombre, contenido_qr)
        self.assertIn("29/09/2026", contenido_qr)
        self.assertIn(factura.codigo_verificacion, contenido_qr)
        self.assertIn(f"{factura.total:,.2f}", contenido_qr)
        self.assertNotIn("http://", contenido_qr)
        self.assertNotIn("https://", contenido_qr)

    def test_el_pdf_incluye_la_imagen_del_qr(self):
        factura = factura_con(2)
        contenido = generar_pdf(factura, ConfiguracionNegocio.cargar())
        self.assertIn(b"/Image", contenido)

    def test_el_pdf_muestra_serie_y_codigo_debajo_del_qr(self):
        factura = factura_con(2)
        contenido = generar_pdf(factura, ConfiguracionNegocio.cargar())
        texto = utiles_pdf.texto_de_pagina(contenido, 0)
        self.assertIn(factura.codigo_verificacion, texto)


class PruebaPdfConTextosLargos(TestCase):
    def test_nombre_de_cliente_muy_largo_no_rompe_el_pdf(self):
        factura = factura_con(4, cliente_nombre="Empresa " + "muy larga " * 20 + "S.A.")
        contenido = generar_pdf(factura, ConfiguracionNegocio.cargar())
        self.assertTrue(contenido.startswith(b"%PDF-"))

    def test_descripcion_de_producto_muy_larga_no_rompe_el_pdf(self):
        factura = crear_factura(
            {
                "fecha": date(2026, 9, 29),
                "cliente_nombre": "Cliente",
            },
            [linea("Producto " + "muy " * 60 + "largo", cantidad="3", precio="12.34")],
        )
        contenido = generar_pdf(factura, ConfiguracionNegocio.cargar())
        self.assertTrue(contenido.startswith(b"%PDF-"))

    def test_factura_de_una_sola_linea(self):
        factura = factura_con(1)
        contenido = generar_pdf(factura, ConfiguracionNegocio.cargar())
        self.assertTrue(contenido.startswith(b"%PDF-"))
        self.assertEqual(utiles_pdf.numero_de_paginas(contenido), 1)

    def test_factura_con_linea_exenta(self):
        factura = crear_factura(
            {
                "fecha": date(2026, 9, 29),
                "cliente_nombre": "Cliente",
            },
            [
                linea("Producto gravado", cantidad="2", precio="19.50"),
                linea("Producto exento", cantidad="1", precio="100.00", gravada=False),
            ],
        )
        contenido = generar_pdf(factura, ConfiguracionNegocio.cargar())
        texto = utiles_pdf.texto_de_pagina(contenido, 0)
        # El exento entra en el subtotal, pero no paga ITBMS:
        # 39.00 + 100.00 = 139.00 y solo los 39.00 son gravados (2.73).
        self.assertIn("139.00", texto)
        self.assertIn("2.73", texto)
        # "Base exenta" ya no se imprime.
        self.assertNotIn("Base exenta", texto)


class PruebaPedidosDelCliente(TestCase):
    """Los cambios que pidio el cliente sobre el PDF."""

    @classmethod
    def setUpTestData(cls):
        cls.configuracion = ConfiguracionNegocio.cargar()
        cls.factura = factura_con(12)
        cls.contenido = generar_pdf(cls.factura, cls.configuracion)
        cls.texto = utiles_pdf.texto_de_pagina(cls.contenido, 0)

    # --- 1. sin descuentos ---

    def test_la_tabla_no_tiene_columna_de_descuento(self):
        self.assertIn("Precio unit.", self.texto)
        for etiqueta in ("Desc.", "Descuento", "Descuentos"):
            self.assertNotIn(etiqueta, self.texto)

    def test_el_descuento_queda_en_cero_en_todas_las_lineas(self):
        for linea in self.factura.lineas.all():
            self.assertEqual(linea.descuento_pct, D("0.00"))

    def test_el_monto_de_cada_linea_es_cantidad_por_precio(self):
        for linea in self.factura.lineas.all():
            self.assertEqual(
                linea.monto,
                (linea.cantidad * linea.precio_unitario).quantize(D("0.01")),
            )

    def test_los_cuadros_de_totales_solo_tienen_tres_filas(self):
        self.assertIn("Subtotal", self.texto)
        self.assertIn("ITBMS 7%", self.texto)
        self.assertIn("Gran total", self.texto)
        for etiqueta in ("Base gravada", "Base exenta", "Portes", "Descuentos"):
            self.assertNotIn(etiqueta, self.texto)

    def test_gran_total_es_subtotal_mas_itbms(self):
        self.assertEqual(
            self.factura.total, self.factura.subtotal + self.factura.itbms
        )

    # --- 4. un solo bloque de notas ---

    def test_el_bloque_de_notas_trae_titulo_y_texto(self):
        self.assertIn("Notas", self.texto)
        self.assertIn("Pago a 30", self.texto)
        self.assertNotIn("Tenga en cuenta", self.texto)

    def test_sin_notas_no_se_imprime_el_bloque(self):
        contenido = generar_pdf(factura_con(4, notas=""), self.configuracion)
        texto = utiles_pdf.texto_de_pagina(contenido, 0)
        self.assertNotIn("Notas", texto)

    def test_no_queda_el_antiguo_texto_de_tenga_en_cuenta(self):
        self.assertNotIn("Tenga en cuenta", self.texto)

    # --- 5. barra con color y menor ---

    def test_la_barra_es_mas_baja_que_antes(self):
        self.assertLess(servicio_pdf.ALTO_BARRA, 24)

    def test_la_barra_no_es_negra(self):
        self.assertNotEqual(
            servicio_pdf._color_hex(self.configuracion.color_barra_factura),
            servicio_pdf.NEGRO,
        )

    def test_el_texto_de_la_barra_contrasta_con_el_fondo(self):
        for fondo, esperado in [("#000000", servicio_pdf.BLANCO),
                                ("#FFFFFF", servicio_pdf.NEGRO)]:
            with self.subTest(fondo=fondo):
                self.assertEqual(
                    servicio_pdf._color_contraste(colors.HexColor(fondo)), esperado
                )

    def test_un_color_de_barra_claro_pone_el_texto_negro(self):
        document = servicio_pdf.PlantillaFactura(
            io.BytesIO(), self.factura, configuracion_con(color_barra_factura="#FBE9A4")
        )
        self.assertEqual(document.color_texto_barra, servicio_pdf.NEGRO)

    # --- 6. espacio y firmas ---

    def _hueco_sobre_la_tabla(self, contenido):
        """Puntos libres entre el bloque del cliente y el encabezado de la tabla.

        Solo mira la columna izquierda: a la derecha van la serie y las fechas,
        que no son el bloque "Facturado a".
        """
        cajas = utiles_pdf.cajas(
            utiles_pdf.texto_normal(utiles_pdf.fragmentos_de_pagina(contenido, 0))
        )
        cabeza = [
            c for c in cajas
            if c[4] in {"N.º", "Producto", "Cant.", "Precio unit.", "Monto"}
        ]
        arriba_tabla = max(c[3] for c in cabeza)
        columna_cliente = [c for c in cajas if c[0] < 400 and c[3] > arriba_tabla + 1]
        return min(c[1] for c in columna_cliente) - arriba_tabla

    def test_el_cliente_largo_deja_entre_8_y_26_puntos(self):
        """Con el bloque del cliente lleno, el hueco es el reservado.

        La columna derecha manda en el hueco final: la OC automatica es
        corta (OC-AAAA-0001), asi que el encabezado termina unas decimas
        arriba y el espacio que sobra es mayor que el de la izquierda.
        """
        factura = factura_con(
            4,
            cliente_nombre=(
                "EMPRESA COMERCIAL DE DISTRIBUCION Y SERVICIOS INTEGRALES "
                "SOCIEDAD ANONIMA DE PANAMA"
            ),
            cliente_ruc="1-2345678-90-123 DV:45",
            cliente_direccion="Avenida Balboa y Calle 50, Ciudad de Panamá",
            cliente_telefono="+507 264-5500",
            cliente_correo="compras@empresa.example",
        )
        hueco = self._hueco_sobre_la_tabla(
            generar_pdf(factura, self.configuracion)
        )
        self.assertGreaterEqual(hueco, 8.0, f"Solo {hueco:.1f} pt de hueco")
        self.assertLessEqual(hueco, 26.0, f"Hueco de {hueco:.1f} pt, sobra espacio")

    def test_el_cliente_corto_nunca_pisa_la_tabla(self):
        hueco = self._hueco_sobre_la_tabla(self.contenido)
        self.assertGreaterEqual(hueco, 8.0, f"Solo {hueco:.1f} pt de hueco")

    def test_las_dos_lineas_de_firma_estan_a_la_misma_altura(self):
        cajas = utiles_pdf.cajas(
            utiles_pdf.texto_normal(utiles_pdf.fragmentos_de_pagina(self.contenido, 0))
        )
        firma = next(c for c in cajas if c[4] == "Firma")
        recibido = next(c for c in cajas if c[4] == "Recibido por")
        self.assertAlmostEqual(firma[1], recibido[1], places=1)
        self.assertAlmostEqual(firma[3], recibido[3], places=1)

    def test_el_vendedor_va_debajo_de_la_firma(self):
        cajas = utiles_pdf.cajas(
            utiles_pdf.texto_normal(utiles_pdf.fragmentos_de_pagina(self.contenido, 0))
        )
        alto = {c[4]: c for c in cajas}
        self.assertIn("María Pérez", alto)
        self.assertIn("(Vendedor)", alto)
        # El nombre va DEBAJO de la linea de firma.
        self.assertLess(alto["María Pérez"][3], alto["Firma"][1])
        self.assertLess(alto["(Vendedor)"][3], alto["María Pérez"][1])

    def test_bajo_el_qr_solo_esta_el_codigo(self):
        # La serie no se repite bajo el QR: sale una vez en la columna derecha
        # y otra en el pie de pagina, que es lo unico esperado.
        veces = self.texto.count(self.factura.numero_serie)
        self.assertLessEqual(veces, 2)
        self.assertIn(self.factura.codigo_verificacion, self.texto)
        # El codigo va en letra pequena (7.5 pt), no en la de la serie (15.5).
        cajas = utiles_pdf.cajas(
            utiles_pdf.texto_normal(utiles_pdf.fragmentos_de_pagina(self.contenido, 0))
        )
        codigo = next(c for c in cajas if c[4] == self.factura.codigo_verificacion)
        serie = next(c for c in cajas if c[4] == self.factura.numero_serie)
        self.assertLess(codigo[3] - codigo[1], serie[3] - serie[1])


class PruebaColoresConfigurables(TestCase):
    """Los tres colores se toman de la configuracion."""

    def _documento(self, **colores):
        return servicio_pdf.PlantillaFactura(
            io.BytesIO(), factura_con(3), configuracion_con(**colores)
        )

    def test_cada_color_tiene_su_propio_campo(self):
        documento = self._documento(
            color_principal="#112233",
            color_barra_factura="#AABBCC",
            color_tabla="#DDEEFF",
        )
        self.assertEqual(documento.color_principal, "#112233")
        self.assertEqual(documento.color_barra.hexval(), "0xaabbcc")
        self.assertEqual(documento.color_tabla.hexval(), "0xddeeff")

    def test_un_color_invalido_cae_en_el_predeterminado(self):
        documento = self._documento(color_barra_factura="no-es-un-color")
        self.assertEqual(
            documento.color_barra.hexval(),
            colors.HexColor(servicio_pdf.COLOR_BARRA).hexval(),
        )

    def test_la_banda_del_gran_total_usa_el_color_de_la_tabla(self):
        documento = self._documento(color_tabla="#DDEEFF")
        self.assertEqual(
            documento.estilos["total_banda"].textColor, servicio_pdf.NEGRO
        )
        self.assertEqual(
            documento.estilos["total_banda_valor"].textColor, servicio_pdf.NEGRO
        )


class PruebaOrdenDeCompraYCondicionEnPdf(TestCase):
    """La OC automatica y el vencimiento (un anio despues) salen en el PDF."""

    @classmethod
    def setUpTestData(cls):
        cls.factura = factura_con(4)
        cls.contenido = generar_pdf(cls.factura, ConfiguracionNegocio.cargar())
        cls.texto = utiles_pdf.texto_de_pagina(cls.contenido, 0)

    def test_lleva_la_orden_de_compra_automatica(self):
        self.assertTrue(self.factura.orden_compra.startswith("OC-2026-"))
        self.assertIn(
            f"Orden de compra: {self.factura.orden_compra}", self.texto
        )

    def test_imprime_el_vencimiento_un_anio_despues(self):
        self.assertIn("Vence: 29/09/2027", self.texto)
        self.assertNotIn("dias de credito", self.texto)

    def test_la_condicion_es_contado_o_credito(self):
        self.assertIn("Condición: Crédito", self.texto)


class PruebaRucOpcionalEnPdf(TestCase):
    """Si se oculta el RUC no se imprime la linea ni queda hueco."""

    def test_sin_ruc_no_aparece_el_texto_ruc(self):
        configuracion = configuracion_con()
        configuracion.empresa_ruc = ""
        contenido = generar_pdf(
            factura_con(2, cliente_ruc="", cliente_direccion=""),
            configuracion,
        )
        texto = utiles_pdf.texto_de_pagina(contenido, 0)
        self.assertNotIn("RUC", texto)
        self.assertIn("CLIENTE DE PRUEBA S.A.", texto)

    def test_ocultar_el_ruc_del_cliente(self):
        factura = factura_con(2, mostrar_ruc=False, cliente_ruc="8-102-456")
        contenido = generar_pdf(factura, ConfiguracionNegocio.cargar())
        self.assertNotIn("8-102-456", utiles_pdf.texto_de_pagina(contenido, 0))

    def test_ocultar_el_ruc_de_la_empresa_quita_la_linea_del_pie(self):
        configuracion = configuracion_con(mostrar_ruc=False)
        configuracion.empresa_ruc = "1-2223333-44-55"
        contenido = generar_pdf(factura_con(2), configuracion)
        paginas = utiles_pdf.textos_por_pagina(contenido)
        texto = " ".join(paginas)
        self.assertNotIn("RUC", texto)

    def test_el_ruc_de_la_empresa_activo_sale_en_el_pie(self):
        configuracion = configuracion_con(mostrar_ruc=True)
        configuracion.empresa_ruc = "1-2223333-44-55"
        contenido = generar_pdf(factura_con(2), configuracion)
        texto = utiles_pdf.texto_de_pagina(contenido, 0)
        self.assertIn("RUC: 1-2223333-44-55", texto)


class PruebaCajaYUnidadEnPdf(TestCase):
    """El PDF muestra la cantidad y el precio con su unidad (und o caja)."""

    @classmethod
    def setUpTestData(cls):
        cls.configuracion = ConfiguracionNegocio.cargar()

    def test_por_unidad_imprime_und_y_precio_de_la_unidad(self):
        factura = crear_factura(
            {
                "fecha": date(2026, 9, 29),
                "cliente_nombre": "Cliente",
            },
            [
                linea(
                    "Papel aluminio 24 und", cantidad="12", precio="12.00",
                    unidades_por_caja=24, cobrar_por="unidad",
                )
            ],
        )
        texto = utiles_pdf.texto_de_pagina(
            generar_pdf(factura, self.configuracion), 0
        )
        # 12 x 12.00 / 24 = 6.00
        self.assertIn("12.00 und", texto)
        self.assertIn("0.50 / und", texto)
        self.assertIn("Caja de 24 und", texto)
        self.assertIn("6.00", texto)

    def test_por_caja_imprime_cajas_y_precio_de_la_caja(self):
        factura = crear_factura(
            {
                "fecha": date(2026, 9, 29),
                "cliente_nombre": "Cliente",
            },
            [
                linea(
                    "Bolsas plásticas medianas 100", cantidad="2", precio="30.00",
                    unidades_por_caja=100, cobrar_por=COBRAR_POR_CAJA,
                )
            ],
        )
        texto = utiles_pdf.texto_de_pagina(
            generar_pdf(factura, self.configuracion), 0
        )
        # 2 cajas x 30.00 = 60.00
        self.assertIn("2.00 cajas", texto)
        self.assertIn("30.00 / caja", texto)
        self.assertIn("Caja de 100 und", texto)
        self.assertIn("60.00", texto)

    def test_una_sola_caja_se_dice_en_singular(self):
        factura = crear_factura(
            {
                "fecha": date(2026, 9, 29),
                "cliente_nombre": "Cliente",
            },
            [
                linea(
                    "Bolsas plásticas medianas 100", cantidad="1", precio="30.00",
                    unidades_por_caja=100, cobrar_por=COBRAR_POR_CAJA,
                )
            ],
        )
        texto = utiles_pdf.texto_de_pagina(
            generar_pdf(factura, self.configuracion), 0
        )
        self.assertIn("1.00 caja", texto)

    def test_factura_mixta_de_40_lineas_sin_solapes(self):
        """Mezcla unidades y cajas: el PDF no se monta por el detalle extra."""
        lineas = []
        for i in range(1, 41):
            datos = {
                "descripcion": PRODUCTOS[(i - 1) % len(PRODUCTOS)],
                "codigo_barras": f"75012345678{i:02d}",
                "categoria": "Alimentos",
                "cantidad": D(str(i % 5 + 1)),
                "precio_unitario": D(f"{10 + i}.{i}0"),
                "gravada": True,
                "unidades_por_caja": 1,
                "cobrar_por": "unidad",
            }
            if i % 10 == 0:
                # Cada decima linea se vende por caja o por unidad con caja.
                if i % 20 == 0:
                    datos["precio_unitario"] = D("30.00")
                    datos["unidades_por_caja"] = 100
                    datos["cobrar_por"] = COBRAR_POR_CAJA
                else:
                    datos["precio_unitario"] = D("12.00")
                    datos["unidades_por_caja"] = 24
                    datos["cobrar_por"] = "unidad"
            lineas.append(datos)

        factura = crear_factura(
            {
                "fecha": date(2026, 9, 29),
                "cliente_nombre": "CLIENTE DE PRUEBA S.A.",
                "cliente_ruc": "1-2345678-90-123",
            },
            lineas,
        )
        contenido = generar_pdf(factura, self.configuracion)
        paginas = utiles_pdf.textos_por_pagina(contenido)
        self.assertGreater(utiles_pdf.numero_de_paginas(contenido), 1)

        todos = " ".join(paginas)
        self.assertIn("Caja de 100 und", todos)
        self.assertIn("Caja de 24 und", todos)
        self.assertIn("30.00 / caja", todos)
        self.assertIn("0.50 / und", todos)

        for indice in range(len(paginas)):
            solapes = utiles_pdf.solapamientos(contenido, indice)
            self.assertEqual(
                solapes, [],
                f"Solapes en la página {indice + 1}: "
                f"{[(a[4], b[4]) for a, b in solapes]}",
            )
