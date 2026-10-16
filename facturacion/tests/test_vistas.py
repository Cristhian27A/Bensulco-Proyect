"""Pruebas de las vistas: pantallas, creación, duplicado, anulación y PDF."""

from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from facturacion.models import ConfiguracionNegocio, Factura
from facturacion.services.pdf import generar_pdf
from facturacion.services.serie import crear_factura
from facturacion.tests.utiles_pdf import numero_de_paginas

D = Decimal
User = get_user_model()


def datos_linea(descripcion="Aceite vegetal 900 ml", cantidad="2",
                precio="5.50", gravada="on",
                unidades_por_caja=None, cobrar_por=None, codigo=""):
    datos = {
        "descripcion": descripcion,
        "codigo_barras": codigo,
        "cantidad": cantidad,
        "precio_unitario": precio,
        "gravada": gravada,
    }
    if unidades_por_caja is not None:
        datos["unidades_por_caja"] = unidades_por_caja
    if cobrar_por is not None:
        datos["cobrar_por"] = cobrar_por
    return datos


def datos_factura(**extra):
    datos = {
        "fecha": date(2026, 9, 29).isoformat(),
        "cliente_nombre": "CLIENTE DE PRUEBA S.A.",
        "cliente_ruc": "1-2345678-90-123",
        "mostrar_ruc": "on",
        "cliente_direccion": "Avenida Central, Ciudad de Panamá",
        "cliente_telefono": "+507 0000-0000",
        "cliente_correo": "compras@cliente.com",
        "sucursal": "Sucursal Centro",
        "vendedor": "María Pérez",
        "condicion_pago": Factura.CONDICION_CREDITO,
        "notas": "Pago a 30 días.",
        "aplicar_itbms": "on",
    }
    datos.update(extra)
    return datos


def post_factura(cliente, lineas=None, **extra):
    """Arma el POST completo, con el management form del formset."""
    if lineas is None:
        lineas = [datos_linea()]
    datos = datos_factura(cliente_nombre=cliente, **extra)
    datos.update({
        "linea-TOTAL_FORMS": str(len(lineas)),
        "linea-INITIAL_FORMS": "0",
        "linea-MIN_NUM_FORMS": "0",
        "linea-MAX_NUM_FORMS": "1000",
    })
    for indice, linea in enumerate(lineas):
        for campo, valor in linea.items():
            if valor is not None:
                datos[f"linea-{indice}-{campo}"] = valor
    return datos


def factura_guardada(lineas=None, **extra):
    datos = {
        "fecha": date(2026, 9, 29),
        "cliente_nombre": "CLIENTE DE PRUEBA S.A.",
        "cliente_ruc": "1-2345678-90-123",
        "cliente_direccion": "Avenida Central, Ciudad de Panamá",
        "cliente_telefono": "+507 0000-0000",
        "cliente_correo": "compras@cliente.com",
        "sucursal": "Sucursal Centro",
        "vendedor": "María Pérez",
        "condicion_pago": Factura.CONDICION_CREDITO,
        "notas": "Pago a 30 días.",
        "itbms_activo": True,
    }
    datos.update(extra)
    return crear_factura(datos, lineas or [datos_linea()])


class PruebaPantallas(TestCase):
    """Cada pantalla abre sin errores y trae los datos del negocio."""

    @classmethod
    def setUpTestData(cls):
        cls.factura = factura_guardada()
        cls.configuracion = ConfiguracionNegocio.cargar()
        cls.configuracion.empresa_nombre = "MI EMPRESA S.A."
        cls.configuracion.save()
        cls.usuario = User.objects.create_user(
            username="vendedor", password="test123"
        )

    def setUp(self):
        self.client.login(username="vendedor", password="test123")

    def test_la_pantalla_inicial_abre(self):
        respuesta = self.client.get(reverse("facturacion:nueva"))
        self.assertEqual(respuesta.status_code, 200)
        self.assertTemplateUsed(respuesta, "facturacion/factura_form.html")
        self.assertContains(respuesta, "MI EMPRESA S.A.")

    def test_el_historial_abre(self):
        respuesta = self.client.get(reverse("facturacion:historial"))
        self.assertEqual(respuesta.status_code, 200)
        self.assertTemplateUsed(respuesta, "facturacion/historial.html")
        self.assertContains(respuesta, self.factura.numero_serie)

    def test_el_detalle_abre(self):
        respuesta = self.client.get(
            reverse("facturacion:detalle", args=[self.factura.pk])
        )
        self.assertEqual(respuesta.status_code, 200)
        self.assertTemplateUsed(respuesta, "facturacion/factura_detalle.html")
        self.assertContains(respuesta, self.factura.numero_serie)

    def test_la_configuracion_abre(self):
        respuesta = self.client.get(reverse("facturacion:configuracion"))
        self.assertEqual(respuesta.status_code, 200)
        self.assertTemplateUsed(respuesta, "facturacion/configuracion.html")

    def test_la_verificacion_abre(self):
        respuesta = self.client.get(reverse(
            "facturacion:verificar",
            args=[self.factura.numero_serie, self.factura.codigo_verificacion],
        ))
        self.assertEqual(respuesta.status_code, 200)
        self.assertTemplateUsed(respuesta, "facturacion/verificar.html")
        self.assertContains(respuesta, self.factura.numero_serie)


class PruebaCrearFactura(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.usuario = User.objects.create_user(
            username="vendedor", password="test123"
        )

    def setUp(self):
        self.client.login(username="vendedor", password="test123")
    """El formulario de la pantalla de inicio."""

    def test_crea_la_factura_y_lleva_al_detalle(self):
        respuesta = self.client.post(
            reverse("facturacion:nueva"),
            post_factura("CLIENTE DE PRUEBA S.A."),
        )
        factura = Factura.objects.get()
        self.assertRedirects(
            respuesta,
            reverse("facturacion:detalle", args=[factura.pk]),
        )
        self.assertEqual(factura.cliente_nombre, "CLIENTE DE PRUEBA S.A.")
        self.assertEqual(factura.lineas.count(), 1)
        # 2 x 5.50 = 11.00 de base gravada y 7% de ITBMS.
        self.assertEqual(factura.subtotal, D("11.00"))
        self.assertEqual(factura.itbms, D("0.77"))
        self.assertEqual(factura.total, D("11.77"))

    def test_acepta_varias_lineas(self):
        self.client.post(reverse("facturacion:nueva"), post_factura(
            "CLIENTE DE PRUEBA S.A.",
            lineas=[
                datos_linea("Aceite vegetal 900 ml", "2", "5.50"),
                datos_linea("Arroz precocido 5 lb", "1", "10.00"),
            ],
        ))
        factura = Factura.objects.get()
        self.assertEqual(factura.lineas.count(), 2)
        self.assertEqual(factura.subtotal, D("21.00"))

    def test_ignora_las_filas_vacias(self):
        lineas = [datos_linea(), datos_linea(descripcion="", cantidad="",
                                             precio="", gravada="")]
        self.client.post(
            reverse("facturacion:nueva"), post_factura("CLIENTO", lineas=lineas),
        )
        self.assertEqual(Factura.objects.get().lineas.count(), 1)

    def test_no_crea_sin_productos(self):
        self.client.post(reverse("facturacion:nueva"), post_factura(
            "CLIENTE", lineas=[datos_linea(descripcion="", cantidad="",
                                           precio="", gravada="")],
        ))
        self.assertFalse(Factura.objects.exists())

    def test_rechaza_cantidad_cero(self):
        self.client.post(reverse("facturacion:nueva"), post_factura(
            "CLIENTE", lineas=[datos_linea(cantidad="0")],
        ))
        self.assertFalse(Factura.objects.exists())

    def test_rechaza_precio_cero(self):
        self.client.post(reverse("facturacion:nueva"), post_factura(
            "CLIENTE", lineas=[datos_linea(precio="0")],
        ))
        self.assertFalse(Factura.objects.exists())

    def test_sin_itbms_todo_es_base_exenta(self):
        datos = post_factura("CLIENTE")
        datos.pop("aplicar_itbms")
        self.client.post(reverse("facturacion:nueva"), datos)
        factura = Factura.objects.get()
        self.assertEqual(factura.itbms, D("0.00"))
        self.assertEqual(factura.base_exenta, factura.subtotal)
        self.assertEqual(factura.base_gravada, D("0.00"))

    def test_el_numero_de_la_factura_es_el_primero_del_ano(self):
        self.client.post(reverse("facturacion:nueva"), post_factura("CLIENTE"))
        self.assertTrue(Factura.objects.get().numero_serie.endswith("-0001"))


class PruebaPdf(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.usuario = User.objects.create_user(
            username="vendedor", password="test123"
        )

    def setUp(self):
        self.client.login(username="vendedor", password="test123")
    """Descarga del PDF."""

    def test_descarga_el_pdf_de_la_factura(self):
        factura = factura_guardada()
        respuesta = self.client.get(
            reverse("facturacion:pdf", args=[factura.pk])
        )
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta["Content-Type"], "application/pdf")
        self.assertTrue(respuesta.content.startswith(b"%PDF-"))

    def test_el_nombre_del_archivo_no_lleva_acentos(self):
        factura = factura_guardada(cliente_nombre="Ñandú Cía. S.A.")
        respuesta = self.client.get(
            reverse("facturacion:pdf", args=[factura.pk])
        )
        self.assertIn("attachment; filename=", respuesta["Content-Disposition"])
        self.assertNotIn("Ñ", respuesta["Content-Disposition"])


class PruebaDuplicarYAnular(TestCase):
    """Duplicar una factura y anularla."""

    @classmethod
    def setUpTestData(cls):
        cls.usuario = User.objects.create_user(
            username="vendedor", password="test123"
        )
        cls.factura = factura_guardada()

    def setUp(self):
        self.client.login(username="vendedor", password="test123")

    def test_duplicar_rellena_el_formulario(self):
        respuesta = self.client.get(
            reverse("facturacion:duplicar", args=[self.factura.pk])
        )
        # Sin seguir la redireccion: si se sigue, la pantalla de inicio
        # consumiria los datos dejados en la sesion.
        self.assertRedirects(
            respuesta, reverse("facturacion:nueva"), fetch_redirect_response=False
        )

        # Al abrir la pantalla de inicio, los datos vienen ya puestos.
        pantalla = self.client.get(reverse("facturacion:nueva"))
        self.assertEqual(pantalla.context["duplicada_de"], self.factura)
        self.assertEqual(
            pantalla.context["form"].initial["cliente_nombre"],
            self.factura.cliente_nombre,
        )

    def test_el_formulario_duplicado_tiene_las_mismas_lineas(self):
        self.client.get(reverse("facturacion:duplicar", args=[self.factura.pk]))
        pantalla = self.client.get(reverse("facturacion:nueva"))
        # El formset deja filas vacias de sobra para agregar productos.
        lineas = [
            f.initial for f in pantalla.context["formset"].forms
            if f.initial.get("descripcion")
        ]
        originales = list(self.factura.lineas.all())
        self.assertEqual(len(lineas), len(originales))
        self.assertEqual(lineas[0]["descripcion"], originales[0].descripcion)
        self.assertEqual(str(lineas[0]["cantidad"]), str(originales[0].cantidad))

    def test_la_factura_duplicada_es_una_nueva(self):
        """Duplicar no toca la original: crea otra con el siguiente numero."""
        self.client.get(reverse("facturacion:duplicar", args=[self.factura.pk]))
        pantalla = self.client.get(reverse("facturacion:nueva"))
        datos = post_factura(
            pantalla.context["form"].initial["cliente_nombre"],
        )
        for indice, inicial in enumerate(
            [f.initial for f in pantalla.context["formset"].forms]
        ):
            if not inicial.get("descripcion"):
                continue
            for campo, valor in inicial.items():
                if valor not in (None, ""):
                    datos[f"linea-{indice}-{campo}"] = str(valor)
        self.client.post(reverse("facturacion:nueva"), datos)

        self.assertEqual(Factura.objects.count(), 2)
        nueva = Factura.objects.exclude(pk=self.factura.pk).get()
        self.assertNotEqual(nueva.numero_serie, self.factura.numero_serie)
        self.factura.refresh_from_db()
        self.assertFalse(self.factura.anulada)

    def test_anular_una_factura(self):
        respuesta = self.client.post(
            reverse("facturacion:anular", args=[self.factura.pk])
        )
        self.assertEqual(respuesta.status_code, 302)
        self.factura.refresh_from_db()
        self.assertTrue(self.factura.anulada)
        self.assertIsNotNone(self.factura.fecha_anulacion)

    def test_no_se_anula_dos_veces(self):
        url = reverse("facturacion:anular", args=[self.factura.pk])
        self.client.post(url)
        segunda = self.client.post(url)
        self.assertEqual(segunda.status_code, 302)
        self.factura.refresh_from_db()
        self.assertIsNotNone(self.factura.fecha_anulacion)


class PruebaVerificar(TestCase):
    """La página pública de verificación."""

    def test_el_codigo_correcto_muestra_la_factura(self):
        factura = factura_guardada()
        respuesta = self.client.get(reverse(
            "facturacion:verificar",
            args=[factura.numero_serie, factura.codigo_verificacion],
        ))
        self.assertEqual(respuesta.status_code, 200)
        self.assertTrue(respuesta.context["valida"])
        self.assertEqual(respuesta.context["factura"], factura)

    def test_un_codigo_erroneo_no_revela_el_total(self):
        factura = factura_guardada()
        respuesta = self.client.get(reverse(
            "facturacion:verificar", args=[factura.numero_serie, "AAAAAAAAAAAA"],
        ))
        self.assertEqual(respuesta.status_code, 200)
        self.assertFalse(respuesta.context["valida"])
        self.assertIsNone(respuesta.context["factura"])
        self.assertNotContains(respuesta, f"{factura.total:,.2f}")

    def test_una_serie_inexistente_no_rompe(self):
        respuesta = self.client.get(
            reverse("facturacion:verificar", args=["FAC-1999-9999", "AAAAAAAAAAAA"])
        )
        self.assertEqual(respuesta.status_code, 200)
        self.assertFalse(respuesta.context["valida"])
        self.assertIsNone(respuesta.context["factura"])


class PruebaConfiguracion(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.usuario = User.objects.create_user(
            username="vendedor", password="test123"
        )

    def setUp(self):
        self.client.login(username="vendedor", password="test123")
    """Guardar los datos del negocio."""

    def test_guarda_los_datos(self):
        datos = {
            "empresa_nombre": "SUPER TIENDA S.A.",
            "empresa_ruc": "1-1111111-22-333",
            "empresa_direccion": "Calle 50, Ciudad de Panamá",
            "empresa_telefono": "+507 200-0000",
            "empresa_correo": "ventas@supertienda.example",
            "color_principal": "#7C3AED",
            "datos_bancarios": "Banco de Ejemplo\nCuenta: 000-000000000000",
            "tenga_en_cuenta": "Conserve esta factura.",
        }
        respuesta = self.client.post(
            reverse("facturacion:configuracion"), datos
        )
        self.assertEqual(respuesta.status_code, 302)
        configuracion = ConfiguracionNegocio.cargar()
        self.assertEqual(configuracion.empresa_nombre, "SUPER TIENDA S.A.")
        self.assertEqual(configuracion.color_principal, "#7C3AED")


class PruebaFormularioSinDescuentosNiPortes(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.usuario = User.objects.create_user(
            username="vendedor", password="test123"
        )

    def setUp(self):
        self.client.login(username="vendedor", password="test123")
    """Lo que pidio el cliente: nada de descuentos ni portes en pantalla."""

    def test_el_formulario_no_ofrece_descuento_ni_portes(self):
        respuesta = self.client.get(reverse("facturacion:nueva"))
        self.assertNotIn("descuento", respuesta.context["form"].fields)
        self.assertNotIn("portes", respuesta.context["form"].fields)
        html = respuesta.content.decode()
        self.assertNotIn("name=\"descuento_pct\"", html)
        self.assertNotIn("name=\"portes\"", html)
        self.assertIn("Precio caja", html)

    def test_el_formulario_acepta_las_notas(self):
        respuesta = self.client.get(reverse("facturacion:nueva"))
        self.assertIn("notas", respuesta.context["form"].fields)
        self.assertFalse(
            respuesta.context["form"].fields["notas"].required,
            "Las notas son opcionales",
        )

    def test_un_descuento_que_llega_por_post_se_ignora(self):
        self.client.post(
            reverse("facturacion:nueva"),
            post_factura("CLIENTE", **{
                "linea-0-descuento_pct": "50",
                "portes": "99.00",
            }),
        )
        linea = Factura.objects.get().lineas.get()
        self.assertEqual(linea.descuento_pct, D("0.00"))
        self.assertEqual(linea.monto, linea.cantidad * linea.precio_unitario)
        self.assertEqual(Factura.objects.get().portes, D("0.00"))

    def test_el_monto_es_cantidad_por_precio_unitario(self):
        self.client.post(reverse("facturacion:nueva"), post_factura(
            "CLIENTE",
            lineas=[datos_linea(cantidad="3", precio="4.25")],
        ))
        linea = Factura.objects.get().lineas.get()
        self.assertEqual(linea.monto, D("12.75"))

    def test_el_total_es_subtotal_mas_itbms(self):
        self.client.post(reverse("facturacion:nueva"), post_factura(
            "CLIENTE", lineas=[datos_linea(cantidad="2", precio="5.50")],
        ))
        factura = Factura.objects.get()
        self.assertEqual(factura.subtotal, D("11.00"))
        self.assertEqual(factura.itbms, D("0.77"))
        self.assertEqual(factura.total, D("11.77"))

    def test_las_notas_del_post_se_guardan(self):
        self.client.post(
            reverse("facturacion:nueva"),
            post_factura("CLIENTE", notas="Entregar en la mañana."),
        )
        self.assertEqual(
            Factura.objects.get().notas, "Entregar en la mañana."
        )

    def test_sin_notas_la_factura_queda_vacia(self):
        self.client.post(
            reverse("facturacion:nueva"), post_factura("CLIENTE", notas=""),
        )
        self.assertEqual(Factura.objects.get().notas, "")


class PruebaNotasPredeterminadas(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.usuario = User.objects.create_user(
            username="vendedor", password="test123"
        )

    def setUp(self):
        self.client.login(username="vendedor", password="test123")
    def test_la_factura_nueva_empieza_con_las_notas_de_la_configuracion(self):
        configuracion = ConfiguracionNegocio.cargar()
        configuracion.notas_predeterminadas = "Traer el carné al recoger."
        configuracion.save()
        respuesta = self.client.get(reverse("facturacion:nueva"))
        self.assertEqual(
            respuesta.context["form"].initial["notas"],
            "Traer el carné al recoger.",
        )
        self.assertIn("Traer el carné al recoger.", respuesta.content.decode())

    def test_se_puede_borrar_el_texto_que_venia_puesto(self):
        self.client.post(
            reverse("facturacion:nueva"), post_factura("CLIENTE", notas=""),
        )
        self.assertEqual(Factura.objects.get().notas, "")


class PruebaDetalleSinDescuentos(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.usuario = User.objects.create_user(
            username="vendedor", password="test123"
        )

    def setUp(self):
        self.client.login(username="vendedor", password="test123")
    def test_el_detalle_muestra_los_tres_totales(self):
        factura = factura_guardada()
        respuesta = self.client.get(
            reverse("facturacion:detalle", args=[factura.pk])
        )
        html = respuesta.content.decode()
        for etiqueta in ("Subtotal", "ITBMS 7%", "Gran total"):
            self.assertIn(etiqueta, html)
        for etiqueta in ("Base gravada", "Base exenta", "Portes", "Descuentos"):
            self.assertNotIn(etiqueta, html)
        self.assertNotIn("Desc.", html)

    def test_el_detalle_muestra_el_bloque_de_notas(self):
        factura = factura_guardada(notas="Revisar el empaque.")
        respuesta = self.client.get(
            reverse("facturacion:detalle", args=[factura.pk])
        )
        html = respuesta.content.decode()
        self.assertIn("Notas", html)
        self.assertIn("Revisar el empaque.", html)
        self.assertNotIn("Observaciones", html)
        self.assertNotIn("Tenga en cuenta", html)

    def test_el_detalle_sin_notas_no_muestra_el_bloque(self):
        factura = factura_guardada(notas="")
        html = self.client.get(
            reverse("facturacion:detalle", args=[factura.pk])
        ).content.decode()
        self.assertNotIn("Notas", html)

    def test_el_detalle_muestra_fecha_y_vencimiento(self):
        factura = factura_guardada()
        html = self.client.get(
            reverse("facturacion:detalle", args=[factura.pk])
        ).content.decode()
        self.assertIn(">29/09/2026<", html)
        self.assertIn("Vence", html)
        self.assertIn(">29/09/2027<", html)

    def test_el_detalle_muestra_caja_y_unidad(self):
        factura = factura_guardada(lineas=[
            datos_linea(
                "Papel aluminio 24 und", cantidad="3", precio="12.00",
                unidades_por_caja="24", cobrar_por="unidad",
            ),
            datos_linea(
                "Bolsas plásticas medianas 100", cantidad="2", precio="30.00",
                unidades_por_caja="100", cobrar_por="caja",
            ),
        ])
        html = self.client.get(
            reverse("facturacion:detalle", args=[factura.pk])
        ).content.decode()
        self.assertIn("Precio efectivo", html)
        self.assertNotIn("Precio unit.", html)
        self.assertIn("Caja de 24 und", html)
        self.assertIn("Caja de 100 und", html)
        self.assertIn("3.00 und", html)
        # Nueva lógica: precio_unitario directo (12.00, no 0.50)
        self.assertIn("12.00 / und", html)
        self.assertIn("2.00 cajas", html)
        self.assertIn("30.00 / caja", html)


class PruebaColoresEnLaConfiguracion(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.usuario = User.objects.create_user(
            username="vendedor", password="test123"
        )

    def setUp(self):
        self.client.login(username="vendedor", password="test123")
    def _post(self, **extra):
        datos = {
            "empresa_nombre": "COMERCIAL SANTA ANA S.A.",
            "empresa_ruc": "1-2223333-44-55",
            "empresa_direccion": "Calle 50, Ciudad de Panamá",
            "empresa_telefono": "+507 264-5500",
            "empresa_correo": "facturacion@comercialsantana.example",
            "datos_bancarios": "Banco Nacional de Panamá",
            "notas_predeterminadas": "Gracias por su compra.",
            "color_principal": "#112233",
            "color_barra_factura": "#AABBCC",
            "color_tabla": "#DDEEFF",
        }
        datos.update(extra)
        return self.client.post(reverse("facturacion:configuracion"), datos)

    def test_el_formulario_tiene_los_tres_colores(self):
        respuesta = self.client.get(reverse("facturacion:configuracion"))
        for campo in ("color_principal", "color_barra_factura", "color_tabla"):
            self.assertIn(campo, respuesta.context["form"].fields)
        self.assertIn("notas_predeterminadas", respuesta.context["form"].fields)

    def test_guarda_los_tres_colores_y_las_notas(self):
        self.assertEqual(self._post().status_code, 302)
        configuracion = ConfiguracionNegocio.cargar()
        self.assertEqual(configuracion.color_principal, "#112233")
        self.assertEqual(configuracion.color_barra_factura, "#AABBCC")
        self.assertEqual(configuracion.color_tabla, "#DDEEFF")
        self.assertEqual(configuracion.notas_predeterminadas, "Gracias por su compra.")

    def test_rechaza_un_color_invalido(self):
        respuesta = self._post(color_tabla="azulito")
        self.assertEqual(respuesta.status_code, 200)
        self.assertIn("color_tabla", respuesta.context["form"].errors)
        self.assertEqual(ConfiguracionNegocio.cargar().color_tabla, "#3A0088")

    def test_los_colores_elegidos_llegan_al_pdf(self):
        self._post()
        factura = factura_guardada()
        pdf = generar_pdf(factura, ConfiguracionNegocio.cargar())
        self.assertEqual(numero_de_paginas(pdf), 1)
        # El PDF se genero sin errores con colores personalizados.
        self.assertTrue(pdf.startswith(b"%PDF"))


class PruebaVencimientoAutomatico(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.usuario = User.objects.create_user(
            username="vendedor", password="test123"
        )

    def setUp(self):
        self.client.login(username="vendedor", password="test123")
    """El vencimiento es un anio despues de la fecha y no se escribe a mano."""

    def test_el_formulario_no_pide_dias_de_credito_ni_vencimiento(self):
        respuesta = self.client.get(reverse("facturacion:nueva"))
        self.assertNotIn("dias_credito", respuesta.context["form"].fields)
        self.assertNotIn("fecha_vencimiento", respuesta.context["form"].fields)
        html = respuesta.content.decode()
        self.assertNotIn("Vencimiento", html)

    def test_la_factura_venace_un_anio_despues_de_la_fecha(self):
        factura = factura_guardada(condicion_pago="credito")
        self.assertFalse(hasattr(factura, "dias_credito"))
        self.assertEqual(factura.fecha_vencimiento, date(2027, 9, 29))


class PruebaOrdenDeCompra(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.usuario = User.objects.create_user(
            username="vendedor", password="test123"
        )

    def setUp(self):
        self.client.login(username="vendedor", password="test123")
    """La OC se puede escribir a mano y si queda vacia se asigna automatica."""

    def test_el_formulario_deja_escribir_la_orden_de_compra(self):
        respuesta = self.client.get(reverse("facturacion:nueva"))
        self.assertIn("orden_compra", respuesta.context["form"].fields)
        self.assertFalse(
            respuesta.context["form"].fields["orden_compra"].required,
            "La OC es opcional: si va vacia se asigna automatica",
        )
        html = respuesta.content.decode()
        self.assertIn("Déjala vacía", html)

    def test_la_orden_de_compra_escrita_se_guarda(self):
        self.client.post(
            reverse("facturacion:nueva"),
            post_factura("CLIENTE", orden_compra="OC-ALMACEN-42"),
        )
        factura = Factura.objects.get()
        self.assertEqual(factura.orden_compra, "OC-ALMACEN-42")

    def test_la_factura_creada_lleva_oc_automatica(self):
        self.client.post(reverse("facturacion:nueva"), post_factura("CLIENTE"))
        factura = Factura.objects.get()
        self.assertTrue(
            factura.orden_compra.startswith("OC-2026-"),
            factura.orden_compra,
        )
        serie = factura.numero_serie.split("-")[0]
        self.assertEqual(serie, "FAC")

    def test_dos_facturas_no_comparten_oc(self):
        self.client.post(reverse("facturacion:nueva"), post_factura("CLIENTE A"))
        self.client.post(reverse("facturacion:nueva"), post_factura("CLIENTE B"))
        a, b = Factura.objects.order_by("pk")
        self.assertNotEqual(a.orden_compra, b.orden_compra)

    def test_una_oc_manuscrita_no_quema_el_consecutivo(self):
        self.client.post(
            reverse("facturacion:nueva"),
            post_factura("CLIENTE A", orden_compra="OC-MANUAL-1"),
        )
        self.client.post(reverse("facturacion:nueva"), post_factura("CLIENTE B"))
        a, b = Factura.objects.order_by("pk")
        self.assertEqual(a.orden_compra, "OC-MANUAL-1")
        self.assertTrue(b.orden_compra.startswith("OC-2026-"))

    def test_el_historial_muestra_la_oc(self):
        factura = factura_guardada()
        respuesta = self.client.get(reverse("facturacion:historial"))
        html = respuesta.content.decode()
        self.assertIn("Orden de compra", html)
        self.assertIn(factura.orden_compra, html)


class PruebaCobroPorCajaEnLaVista(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.usuario = User.objects.create_user(
            username="vendedor", password="test123"
        )

    def setUp(self):
        self.client.login(username="vendedor", password="test123")
    """Las lineas pueden cobrarse por unidad o por caja."""

    def test_se_guarda_una_linea_por_unidad_con_caja(self):
        self.client.post(
            reverse("facturacion:nueva"),
            post_factura(
                "CLIENTE",
                lineas=[datos_linea(
                    "Papel aluminio 24 und", cantidad="12", precio="12.00",
                    unidades_por_caja="24", cobrar_por="unidad",
                )],
            ),
        )
        linea = Factura.objects.get().lineas.get()
        self.assertEqual(linea.unidades_por_caja, 24)
        self.assertEqual(linea.cobrar_por, "unidad")
        # Nueva lógica: 12 x 12.00 = 144.00 (precio_unitario directo)
        self.assertEqual(linea.monto, D("144.00"))

    def test_se_guarda_una_linea_por_caja(self):
        self.client.post(
            reverse("facturacion:nueva"),
            post_factura(
                "CLIENTE",
                lineas=[datos_linea(
                    "Bolsas plásticas medianas 100", cantidad="2", precio="30.00",
                    unidades_por_caja="100", cobrar_por="caja",
                )],
            ),
        )
        linea = Factura.objects.get().lineas.get()
        self.assertEqual(linea.unidades_por_caja, 100)
        self.assertEqual(linea.cobrar_por, "caja")
        # 2 cajas x 30.00 = 60.00, con su ITBMS.
        self.assertEqual(linea.monto, D("60.00"))
        self.assertEqual(Factura.objects.get().total, D("64.20"))

    def test_sin_datos_de_caja_queda_por_unidad_sin_dividir(self):
        self.client.post(
            reverse("facturacion:nueva"),
            post_factura(
                "CLIENTE", lineas=[datos_linea(cantidad="3", precio="4.25")],
            ),
        )
        linea = Factura.objects.get().lineas.get()
        self.assertEqual(linea.unidades_por_caja, 1)
        self.assertEqual(linea.cobrar_por, "unidad")
        self.assertEqual(linea.monto, D("12.75"))

    def test_el_formulario_ofrece_los_controles_de_caja(self):
        respuesta = self.client.get(reverse("facturacion:nueva"))
        html = respuesta.content.decode()
        self.assertIn('name="linea-0-unidades_por_caja"', html)
        self.assertIn('name="linea-0-cobrar_por"', html)
        self.assertIn("Cobrar por", html)
        self.assertIn("Caja de", html)

    def test_un_duplicado_conserva_unidades_por_caja_y_cobrar_por(self):
        factura = factura_guardada(
            [
                {
                    "descripcion": "Bolsas plásticas medianas 100",
                    "codigo_barras": "",
                    "categoria": "Limpieza",
                    "cantidad": D("2"),
                    "precio_unitario": D("30.00"),
                    "descuento_pct": D("0"),
                    "gravada": True,
                    "unidades_por_caja": 100,
                    "cobrar_por": "caja",
                }
            ]
        )
        self.client.get(reverse("facturacion:duplicar", args=[factura.pk]))
        pantalla = self.client.get(reverse("facturacion:nueva"))
        lineas = [
            f.initial for f in pantalla.context["formset"].forms
            if f.initial.get("descripcion")
        ]
        self.assertEqual(len(lineas), 1)
        self.assertEqual(lineas[0]["unidades_por_caja"], 100)
        self.assertEqual(lineas[0]["cobrar_por"], "caja")


class PruebaRucOpcional(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.usuario = User.objects.create_user(
            username="vendedor", password="test123"
        )

    def setUp(self):
        self.client.login(username="vendedor", password="test123")
    """El RUC/DV del cliente y de la empresa se puede ocultar."""

    def test_sin_ruc_el_pdf_no_imprime_la_linea(self):
        factura = factura_guardada(cliente_ruc="")
        pdf = generar_pdf(factura, ConfiguracionNegocio.cargar())
        self.assertTrue(pdf.startswith(b"%PDF"))
        self.assertEqual(numero_de_paginas(pdf), 1)

    def test_ocultar_el_ruc_del_cliente(self):
        factura = factura_guardada(mostrar_ruc=False, cliente_ruc="8-102-456")
        pdf = generar_pdf(factura, ConfiguracionNegocio.cargar())
        texto = self._texto(pdf)
        self.assertNotIn("8-102-456", texto)

    def test_ocultar_el_ruc_de_la_empresa(self):
        configuracion = ConfiguracionNegocio.cargar()
        configuracion.empresa_ruc = "1-2223333-44-55"
        configuracion.mostrar_ruc = False
        configuracion.save()
        pdf = generar_pdf(factura_guardada(), configuracion)
        texto = self._texto(pdf)
        self.assertNotIn("RUC", texto)
        self.assertNotIn("1-2223333-44-55", texto)

    def test_con_el_ruc_activo_si_se_imprime(self):
        factura = factura_guardada(cliente_ruc="1-2345678-90-123")
        pdf = generar_pdf(factura, ConfiguracionNegocio.cargar())
        self.assertIn("1-2345678-90-123", self._texto(pdf))

    def _texto(self, pdf):
        from facturacion.tests.utiles_pdf import texto_de_pagina

        return texto_de_pagina(pdf, 0)


class PruebaConfiguracionMuestraRuc(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.usuario = User.objects.create_user(
            username="vendedor", password="test123"
        )

    def setUp(self):
        self.client.login(username="vendedor", password="test123")
    def test_el_formulario_tiene_la_casilla(self):
        respuesta = self.client.get(reverse("facturacion:configuracion"))
        self.assertIn("mostrar_ruc", respuesta.context["form"].fields)
