"""Pruebas de modelos, series consecutivas y codigo de verificacion."""

from datetime import date, timedelta
from decimal import Decimal

from django.db import IntegrityError, transaction
from django.test import TestCase

from facturacion.models import (
    ConfiguracionNegocio,
    ContadorOrdenCompra,
    ContadorSerie,
    COBRAR_POR_CAJA,
    COBRAR_POR_UNIDAD,
    Factura,
)
from facturacion.services.serie import (
    anular_factura,
    crear_factura,
    generar_codigo_verificacion,
    siguiente_numero_orden,
    siguiente_numero_serie,
    verificar_codigo,
)

D = Decimal


def datos_cliente(**extra):
    base = {
        "fecha": date(2026, 9, 29),
        "cliente_nombre": "CLIENTE DE PRUEBA S.A.",
        "cliente_ruc": "1-2345678-90",
        "vendedor": "Vendedor de Prueba",
    }
    base.update(extra)
    return base


def lineas_de_ejemplo(cantidad=2):
    return [
        {
            "descripcion": "Producto de prueba",
            "codigo_barras": "1234567890",
            "categoria": "General",
            "cantidad": D(cantidad),
            "precio_unitario": D("8.75"),
            "descuento_pct": D("3"),
            "gravada": True,
        }
    ]


class PruebasConfiguracionNegocio(TestCase):
    def test_cargar_crea_una_sola_fila(self):
        primero = ConfiguracionNegocio.cargar()
        segundo = ConfiguracionNegocio.cargar()
        self.assertEqual(primero.pk, 1)
        self.assertEqual(ConfiguracionNegocio.objects.count(), 1)
        self.assertEqual(primero.pk, segundo.pk)

    def test_los_valores_iniciales_son_de_ejemplo(self):
        config = ConfiguracionNegocio.cargar()
        self.assertIn("EJEMPLO", config.empresa_nombre)
        self.assertIn("EJEMPLO", config.empresa_ruc)
        self.assertTrue(config.notas_predeterminadas)
        self.assertEqual(config.color_principal, "#3A0088")
        self.assertEqual(config.color_barra_factura, "#5B3A9E")
        self.assertEqual(config.color_tabla, "#3A0088")

    def test_guardar_fuerza_la_misma_fila(self):
        config = ConfiguracionNegocio.cargar()
        otra = ConfiguracionNegocio(empresa_nombre="Otra", empresa_ruc="9-9")
        otra.save()
        self.assertEqual(ConfiguracionNegocio.objects.count(), 1)
        self.assertEqual(ConfiguracionNegocio.objects.get().empresa_nombre, "Otra")
        self.assertNotEqual(config.pk, None)

    def test_no_se_puede_borrar(self):
        config = ConfiguracionNegocio.cargar()
        config.delete()
        self.assertEqual(ConfiguracionNegocio.objects.count(), 1)


class PruebasNumeroDeSerie(TestCase):
    def test_formato_y_consecutivo_del_primer_anio(self):
        with transaction.atomic():
            self.assertEqual(siguiente_numero_serie(date(2026, 1, 5)), "FAC-2026-0001")
            self.assertEqual(siguiente_numero_serie(date(2026, 1, 5)), "FAC-2026-0002")
            self.assertEqual(siguiente_numero_serie(date(2026, 12, 31)), "FAC-2026-0003")

    def test_el_consecutivo_se_reinicia_cada_anio(self):
        with transaction.atomic():
            siguiente_numero_serie(date(2025, 6, 1))
            siguiente_numero_serie(date(2025, 6, 1))
        with transaction.atomic():
            self.assertEqual(siguiente_numero_serie(date(2026, 1, 1)), "FAC-2026-0001")

    def test_numero_de_cuatro_digitos_a_partir_de_9999(self):
        ContadorSerie.objects.create(anio=2026, ultimo_numero=9998)
        with transaction.atomic():
            self.assertEqual(siguiente_numero_serie(date(2026, 1, 1)), "FAC-2026-9999")
            self.assertEqual(siguiente_numero_serie(date(2026, 1, 1)), "FAC-2026-10000")

    def test_facturas_reales_generan_series_unicas_y_consecutivas(self):
        for _ in range(5):
            crear_factura(datos_cliente(), lineas_de_ejemplo())
        series = list(
            Factura.objects.order_by("numero_serie").values_list("numero_serie", flat=True)
        )
        self.assertEqual(
            series,
            ["FAC-2026-0001", "FAC-2026-0002", "FAC-2026-0003", "FAC-2026-0004", "FAC-2026-0005"],
        )
        self.assertEqual(Factura.objects.filter(numero_serie="FAC-2026-0001").count(), 1)

    def test_el_serie_es_unico_en_la_base(self):
        Factura.objects.create(
            numero_serie="FAC-2026-0001", codigo_verificacion="ABCDEFGH2345",
            fecha=date(2026, 1, 1),
            cliente_nombre="X",
        )
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Factura.objects.create(
                    numero_serie="FAC-2026-0001", codigo_verificacion="OTRO1234567",
                    fecha=date(2026, 1, 1),
                    cliente_nombre="Y",
                )

    def test_dos_anios_distintos_no_se_pisan(self):
        crear_factura(datos_cliente(fecha=date(2026, 1, 1)), lineas_de_ejemplo())
        crear_factura(datos_cliente(fecha=date(2027, 1, 1)), lineas_de_ejemplo())
        series = set(Factura.objects.values_list("numero_serie", flat=True))
        self.assertEqual(series, {"FAC-2026-0001", "FAC-2027-0001"})


class PruebasCodigoVerificacion(TestCase):
    def setUp(self):
        self.fecha = date(2026, 9, 29)
        self.serie = "FAC-2026-0001"
        self.total = D("258.81")

    def test_tiene_doce_caracteres_en_mayusculas(self):
        codigo = generar_codigo_verificacion(self.serie, self.total, self.fecha)
        self.assertEqual(len(codigo), 12)
        self.assertEqual(codigo, codigo.upper())
        self.assertTrue(codigo.isalnum())

    def test_es_estable_para_la_misma_factura(self):
        primero = generar_codigo_verificacion(self.serie, self.total, self.fecha)
        segundo = generar_codigo_verificacion(self.serie, self.total, self.fecha)
        self.assertEqual(primero, segundo)

    def test_cambia_si_cambia_el_monto_la_serie_o_la_fecha(self):
        base = generar_codigo_verificacion(self.serie, self.total, self.fecha)
        self.assertNotEqual(base, generar_codigo_verificacion("FAC-2026-0002", self.total, self.fecha))
        self.assertNotEqual(base, generar_codigo_verificacion(self.serie, D("258.82"), self.fecha))
        self.assertNotEqual(
            base,
            generar_codigo_verificacion(self.serie, self.total, self.fecha + timedelta(days=1)),
        )

    def test_verificar_acepta_el_codigo_bueno_y_rechaza_el_malo(self):
        codigo = generar_codigo_verificacion(self.serie, self.total, self.fecha)
        self.assertTrue(verificar_codigo(self.serie, codigo, self.total, self.fecha))
        self.assertFalse(verificar_codigo(self.serie, "XXXXXXXXXXXX", self.total, self.fecha))
        self.assertFalse(verificar_codigo("", codigo, self.total, self.fecha))
        self.assertFalse(verificar_codigo(self.serie, "", self.total, self.fecha))

    def test_la_factura_guardada_lleva_el_codigo_correcto(self):
        factura = crear_factura(datos_cliente(), lineas_de_ejemplo())
        esperado = generar_codigo_verificacion(
            factura.numero_serie, factura.total, factura.fecha
        )
        self.assertEqual(factura.codigo_verificacion, esperado)
        self.assertEqual(len(factura.codigo_verificacion), 12)


class PruebasCrearFactura(TestCase):
    def test_guarda_las_lineas_calculadas(self):
        factura = crear_factura(datos_cliente(), lineas_de_ejemplo(cantidad=2))
        linea = factura.lineas.get()
        self.assertEqual(linea.orden, 1)
        self.assertEqual(linea.descripcion, "Producto de prueba")
        self.assertEqual(linea.codigo_barras, "1234567890")
        self.assertEqual(linea.categoria, "General")
        # Sin descuentos: el monto es 2 x 8.75 = 17.50
        self.assertEqual(linea.descuento_pct, D("0.00"))
        self.assertEqual(linea.monto, D("17.50"))
        self.assertEqual(factura.subtotal, D("17.50"))
        self.assertEqual(factura.descuento_total, D("0.00"))
        self.assertEqual(factura.base_gravada, D("17.50"))
        self.assertEqual(factura.itbms, D("1.23"))
        self.assertEqual(factura.total, D("18.73"))

    def test_total_en_letras_del_modelo(self):
        factura = crear_factura(datos_cliente(), lineas_de_ejemplo())
        # 2 x 8.75 = 17.50 + 7% = 18.73
        self.assertEqual(factura.total, D("18.73"))
        self.assertEqual(factura.total_en_letras, "DIECIOCHO CON 73/100 DÓLARES")

    def test_orden_de_las_lineas_se_respeta(self):
        lineas = [
            dict(lineas_de_ejemplo()[0], descripcion=f"Producto {i}", cantidad=D("1"))
            for i in range(1, 6)
        ]
        factura = crear_factura(datos_cliente(), lineas)
        self.assertEqual(
            [linea.descripcion for linea in factura.lineas.all()],
            ["Producto 1", "Producto 2", "Producto 3", "Producto 4", "Producto 5"],
        )

    def test_la_condicion_de_pago_se_lee_en_claro(self):
        credito = crear_factura(
            datos_cliente(condicion_pago="credito"),
            lineas_de_ejemplo(),
        )
        contado = crear_factura(
            datos_cliente(condicion_pago="contado"),
            lineas_de_ejemplo(),
        )
        self.assertEqual(credito.condicion_pago, Factura.CONDICION_CREDITO)
        self.assertEqual(credito.texto_condicion_pago, "Crédito")
        self.assertEqual(contado.texto_condicion_pago, "Contado")

    def test_anular_marca_el_estado_y_la_fecha(self):
        factura = crear_factura(datos_cliente(), lineas_de_ejemplo())
        self.assertFalse(factura.anulada)
        anular_factura(factura)
        factura.refresh_from_db()
        self.assertTrue(factura.anulada)
        self.assertIsNotNone(factura.fecha_anulacion)

    def test_una_factura_anulada_consume_serie_nueva(self):
        factura = crear_factura(datos_cliente(), lineas_de_ejemplo())
        anular_factura(factura)
        nueva = crear_factura(datos_cliente(), lineas_de_ejemplo())
        self.assertNotEqual(factura.numero_serie, nueva.numero_serie)


class PruebasOrdenDeCompra(TestCase):
    """La OC es automatica: OC-AAAA-0001, con su propio contador."""

    def test_formato_y_consecutivo_por_anio(self):
        with transaction.atomic():
            self.assertEqual(
                siguiente_numero_orden(date(2026, 3, 1)), "OC-2026-0001"
            )
            self.assertEqual(
                siguiente_numero_orden(date(2026, 12, 31)), "OC-2026-0002"
            )
        with transaction.atomic():
            self.assertEqual(
                siguiente_numero_orden(date(2027, 1, 1)), "OC-2027-0001"
            )

    def test_el_contador_va_aparte_del_de_la_serie(self):
        with transaction.atomic():
            self.assertEqual(
                siguiente_numero_orden(date(2026, 3, 1)), "OC-2026-0001"
            )
            self.assertEqual(siguiente_numero_serie(date(2026, 3, 1)), "FAC-2026-0001")

    def test_las_facturas_reciben_oc_consecutivas_y_unicas(self):
        facturas = [
            crear_factura(datos_cliente(), lineas_de_ejemplo()) for _ in range(3)
        ]
        ordenes = [f.orden_compra for f in facturas]
        self.assertEqual(ordenes, ["OC-2026-0001", "OC-2026-0002", "OC-2026-0003"])
        self.assertEqual(len(set(ordenes)), len(ordenes))

    def test_una_factura_anulada_no_libera_su_oc(self):
        factura = crear_factura(datos_cliente(), lineas_de_ejemplo())
        anular_factura(factura)
        nueva = crear_factura(datos_cliente(), lineas_de_ejemplo())
        self.assertEqual(factura.orden_compra, "OC-2026-0001")
        self.assertEqual(nueva.orden_compra, "OC-2026-0002")
        self.assertNotEqual(factura.orden_compra, nueva.orden_compra)

    def test_se_puede_ahorrar_el_contador_de_oc_con_datos_existentes(self):
        """Las facturas antiguas con OC manual se conservan tal cual."""
        factura = crear_factura(
            datos_cliente(), lineas_de_ejemplo()
        )
        ContadorOrdenCompra.objects.filter(anio=2026).update(ultimo_numero=187)
        nueva = crear_factura(datos_cliente(), lineas_de_ejemplo())
        self.assertTrue(factura.orden_compra.startswith("OC-2026-"))
        self.assertEqual(nueva.orden_compra, "OC-2026-0188")

    def test_se_puede_escribir_la_oc_a_mano(self):
        factura = crear_factura(
            datos_cliente(orden_compra="OC-CLIENTE-007"), lineas_de_ejemplo()
        )
        factura.refresh_from_db()
        self.assertEqual(factura.orden_compra, "OC-CLIENTE-007")

    def test_la_oc_manuscrita_no_quema_el_consecutivo_automatico(self):
        crear_factura(
            datos_cliente(orden_compra="OC-MANUAL-1"), lineas_de_ejemplo()
        )
        siguiente = crear_factura(datos_cliente(), lineas_de_ejemplo())
        self.assertEqual(siguiente.orden_compra, "OC-2026-0001")

    def test_la_oc_en_blanco_se_asigna_automatica(self):
        factura = crear_factura(datos_cliente(orden_compra="  "), lineas_de_ejemplo())
        self.assertTrue(factura.orden_compra.startswith("OC-2026-"))


class PruebasCajaYUnidadAlGuardar(TestCase):
    """El precio se guarda por la caja; el cobro puede ser por unidad o caja."""

    def test_guardar_persiste_unidades_por_caja_y_cobrar_por(self):
        factura = crear_factura(
            datos_cliente(),
            [
                {
                    "descripcion": "Bolsas plásticas 100",
                    "codigo_barras": "",
                    "categoria": "Limpieza",
                    "cantidad": D("2"),
                    "precio_unitario": D("30.00"),
                    "descuento_pct": D("0"),
                    "gravada": True,
                    "unidades_por_caja": 100,
                    "cobrar_por": COBRAR_POR_CAJA,
                }
            ],
        )
        linea = factura.lineas.get()
        self.assertEqual(linea.unidades_por_caja, 100)
        self.assertEqual(linea.cobrar_por, COBRAR_POR_CAJA)
        # 2 cajas x 30.00 = 60.00
        self.assertEqual(linea.monto, D("60.00"))

    def test_monto_por_unidad_se_calcula_dividiendo_la_caja(self):
        factura = crear_factura(
            datos_cliente(),
            [
                {
                    "descripcion": "Papel aluminio 24 und",
                    "codigo_barras": "",
                    "categoria": "Abarrotes",
                    "cantidad": D("12"),
                    "precio_unitario": D("12.00"),
                    "descuento_pct": D("0"),
                    "gravada": True,
                    "unidades_por_caja": 24,
                    "cobrar_por": COBRAR_POR_UNIDAD,
                }
            ],
        )
        linea = factura.lineas.get()
        self.assertEqual(linea.unidades_por_caja, 24)
        self.assertEqual(linea.cobrar_por, COBRAR_POR_UNIDAD)
        # 12 x 12.00 / 24 = 6.00
        self.assertEqual(linea.monto, D("6.00"))
        self.assertEqual(factura.total, D("6.42"))

    def test_sin_datos_de_caja_queda_por_unidad_y_sin_dividir(self):
        factura = crear_factura(datos_cliente(), lineas_de_ejemplo())
        linea = factura.lineas.get()
        self.assertEqual(linea.unidades_por_caja, 1)
        self.assertEqual(linea.cobrar_por, COBRAR_POR_UNIDAD)
        self.assertEqual(linea.monto, D("17.50"))
