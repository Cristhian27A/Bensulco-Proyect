"""Pruebas del cálculo de montos y del redondeo."""

from decimal import Decimal

from django.test import SimpleTestCase

from facturacion.services.totales import (
    COBRAR_POR_CAJA,
    COBRAR_POR_UNIDAD,
    calcular_linea,
    calcular_totales,
    formato_precio,
    monto_linea,
    precio_efectivo,
    precio_por_unidad,
    redondear,
)

D = Decimal


class PruebasMontosDeLinea(SimpleTestCase):
    def test_ejemplo_8_75_por_2_con_3_porciento(self):
        self.assertEqual(monto_linea(D("8.75"), D("2"), D("3")), D("16.98"))

    def test_ejemplo_19_50_con_5_porciento(self):
        self.assertEqual(monto_linea(D("19.50"), D("1"), D("5")), D("18.53"))

    def test_redondeo_half_up_empuja_el_5_hacia_arriba(self):
        # 2.345 con 0% debe dar 2.35, no 2.34
        self.assertEqual(monto_linea(D("1"), D("2.345")), D("2.35"))
        # 0.005 con 0% sube a 0.01
        self.assertEqual(monto_linea(D("1"), D("0.005")), D("0.01"))

    def test_sin_descuento_es_cantidad_por_precio(self):
        self.assertEqual(monto_linea(D("3"), D("4.25")), D("12.75"))

    def test_descuento_de_cien_porciento_deja_cero(self):
        self.assertEqual(monto_linea(D("10"), D("10"), D("100")), D("0.00"))

    def test_cantidad_o_precio_negativo_no_produce_monto_negativo(self):
        self.assertEqual(monto_linea(D("0"), D("10")), D("0.00"))
        self.assertEqual(monto_linea(D("2"), D("-5")), D("0.00"))

    def test_acepta_floats_sin_arrastrar_error(self):
        # 0.1 + 0.2 en float da 0.30000000000000004; con Decimal no.
        self.assertEqual(monto_linea(0.1, 3), D("0.30"))

    def test_redondear_usa_dos_decimales(self):
        self.assertEqual(redondear("12.345"), D("12.35"))
        self.assertEqual(redondear(D("10")), D("10.00"))


class PruebasTotales(SimpleTestCase):
    def lineas(self):
        return [
            {"cantidad": D("2"), "precio_unitario": D("8.75"), "descuento_pct": D("3"), "gravada": True},
            {"cantidad": D("1"), "precio_unitario": D("19.50"), "descuento_pct": D("5"), "gravada": True},
        ]

    def test_subtotal_menos_descuento_igual_a_base(self):
        totales = calcular_totales(self.lineas())
        self.assertEqual(totales.subtotal, D("37.00"))
        self.assertEqual(totales.base_gravada, D("35.51"))
        self.assertEqual(totales.descuento_total, D("1.49"))
        # La invariante que se pide: cuadra exacto al centavo.
        self.assertEqual(
            totales.subtotal - totales.descuento_total,
            totales.base_gravada + totales.base_exenta,
        )

    def test_itbms_solo_sobre_lineas_gravadas(self):
        totales = calcular_totales(self.lineas())
        self.assertEqual(totales.itbms, redondear(totales.base_gravada * D("0.07")))
        self.assertEqual(totales.base_exenta, D("0.00"))

    def test_total_es_base_mas_itbms_mas_portes(self):
        totales = calcular_totales(self.lineas(), portes=D("5.50"))
        esperado = totales.base_gravada + totales.base_exenta + totales.itbms + D("5.50")
        self.assertEqual(totales.total, redondear(esperado))
        self.assertEqual(totales.total, D("43.50"))  # 35.51 + 2.49 + 5.50

    def test_linea_exenta_no_paga_itbms(self):
        lineas = [
            {"cantidad": D("1"), "precio_unitario": D("100"), "descuento_pct": D("0"), "gravada": True},
            {"cantidad": D("1"), "precio_unitario": D("50"), "descuento_pct": D("0"), "gravada": False},
        ]
        totales = calcular_totales(lineas)
        self.assertEqual(totales.base_gravada, D("100.00"))
        self.assertEqual(totales.base_exenta, D("50.00"))
        self.assertEqual(totales.itbms, D("7.00"))
        self.assertEqual(totales.total, D("157.00"))

    def test_invariante_cumple_en_cien_lineas_aleatorias(self):
        import random

        azar = random.Random(20260929)
        for _ in range(100):
            lineas = []
            for _i in range(azar.randint(1, 12)):
                lineas.append({
                    "cantidad": D(azar.randint(1, 50)),
                    "precio_unitario": D(azar.randint(1, 99999)) / D(100),
                    "descuento_pct": D(azar.choice([0, 1, 3, 5, 7.5, 10, 12.5, 15, 33.33])),
                    "gravada": azar.random() > 0.2,
                })
            totales = calcular_totales(lineas, portes=D(azar.randint(0, 5000)) / D(100))
            base = totales.base_gravada + totales.base_exenta
            self.assertEqual(totales.subtotal - totales.descuento_total, base)
            self.assertEqual(totales.total, redondear(base + totales.itbms + totales.portes))
            for linea in totales.lineas:
                self.assertEqual(linea.monto, linea.monto.quantize(D("0.01")))

    def test_sin_lineas_da_todo_en_cero(self):
        totales = calcular_totales([])
        self.assertEqual(totales.subtotal, D("0.00"))
        self.assertEqual(totales.total, D("0.00"))

    def test_itbms_desactivado_pone_todo_en_exenta(self):
        totales = calcular_totales(self.lineas(), itbms_activo=False)
        self.assertEqual(totales.itbms, D("0.00"))
        self.assertEqual(totales.base_exenta, D("35.51"))
        self.assertEqual(totales.base_gravada, D("0.00"))

    def test_acepta_objetos_con_atributos(self):
        class Linea:
            cantidad = D("2")
            precio_unitario = D("8.75")
            descuento_pct = D("3")
            gravada = True

        totales = calcular_totales([Linea()])
        self.assertEqual(totales.lineas[0].monto, D("16.98"))

    def test_texto_formateado_lista_para_la_pantalla(self):
        texto = calcular_totales(self.lineas()).como_texto()
        self.assertEqual(texto["subtotal"], "37.00")
        self.assertEqual(texto["total"], "38.00")  # 35.51 + 2.49


class PruebasCobroPorCajaYUnidad(SimpleTestCase):
    """El precio se guarda por la caja entera; el monto puede cobrar por
    unidad (se divide entre las unidades de la caja) o por caja."""

    CAJA_24 = D("30.00")  # caja de 24 a 30.00
    CAJA_3 = D("10.00")   # caja de 3 a 10.00

    def test_precio_de_la_unidad_es_el_de_la_caja_dividido(self):
        self.assertEqual(precio_por_unidad(self.CAJA_24, 24), D("1.25"))
        # 10 / 3 no es exacto y no se redondea hasta el monto.
        self.assertEqual(precio_por_unidad(self.CAJA_3, 3), D("3.333333333333333333333333333"))

    def test_precio_efectivo_por_unidad_y_por_caja(self):
        self.assertEqual(
            precio_efectivo(self.CAJA_24, 24, COBRAR_POR_UNIDAD), D("1.25")
        )
        self.assertEqual(
            precio_efectivo(self.CAJA_24, 24, COBRAR_POR_CAJA), D("30.00")
        )

    def test_ejemplos_del_cliente_caja_de_24(self):
        # 12 und -> 12 x 30 / 24 = 15.00
        self.assertEqual(
            monto_linea(D("12"), self.CAJA_24, unidades_por_caja=24), D("15.00")
        )
        # 24 und -> 24 x 30 / 24 = 30.00
        self.assertEqual(
            monto_linea(D("24"), self.CAJA_24, unidades_por_caja=24), D("30.00")
        )
        # 1 caja -> 1 x 30 = 30.00
        self.assertEqual(
            monto_linea(D("1"), self.CAJA_24, unidades_por_caja=24,
                        cobrar_por=COBRAR_POR_CAJA),
            D("30.00"),
        )
        # 2 cajas -> 2 x 30 = 60.00
        self.assertEqual(
            monto_linea(D("2"), self.CAJA_24, unidades_por_caja=24,
                        cobrar_por=COBRAR_POR_CAJA),
            D("60.00"),
        )
        # 30 und -> 30 x 30 / 24 = 37.50
        self.assertEqual(
            monto_linea(D("30"), self.CAJA_24, unidades_por_caja=24), D("37.50")
        )

    def test_caja_que_no_divide_exacto_redondea_una_sola_vez(self):
        # 5 und de una caja de 3 a 10.00 -> 16.666... -> 16.67
        self.assertEqual(
            monto_linea(D("5"), self.CAJA_3, unidades_por_caja=3), D("16.67")
        )

    def test_calcular_linea_guarda_los_datos_de_la_caja(self):
        linea = calcular_linea(
            D("12"), self.CAJA_24, unidades_por_caja=24,
            cobrar_por=COBRAR_POR_UNIDAD,
        )
        self.assertEqual(linea.monto, D("15.00"))
        self.assertEqual(linea.unidades_por_caja, 24)
        self.assertEqual(linea.cobrar_por, COBRAR_POR_UNIDAD)
        self.assertEqual(linea.precio_para_mostrar, D("1.25"))
        # El bruto es el precio mostrado por la cantidad, sin redondear.
        self.assertEqual(linea.bruto, D("15.00"))

    def test_calcular_totales_respeta_caja_y_unidad_de_cada_item(self):
        lineas = [
            {"cantidad": D("12"), "precio_unitario": self.CAJA_24,
             "descuento_pct": D("0"), "gravada": True,
             "unidades_por_caja": 24, "cobrar_por": COBRAR_POR_UNIDAD},
            {"cantidad": D("2"), "precio_unitario": self.CAJA_24,
             "descuento_pct": D("0"), "gravada": True,
             "unidades_por_caja": 24, "cobrar_por": COBRAR_POR_CAJA},
        ]
        totales = calcular_totales(lineas)
        self.assertEqual(totales.lineas[0].monto, D("15.00"))
        self.assertEqual(totales.lineas[1].monto, D("60.00"))
        self.assertEqual(totales.subtotal, D("75.00"))
        # La invariante sigue cuadrando al centavo.
        self.assertEqual(
            totales.subtotal - totales.descuento_total,
            totales.base_gravada + totales.base_exenta,
        )

    def test_invariante_con_cajas_en_cien_casos_aleatorios(self):
        import random

        azar = random.Random(20261002)
        for _ in range(100):
            lineas = []
            for _i in range(azar.randint(1, 12)):
                unidades = azar.choice([1, 3, 6, 12, 24, 100])
                cobrar_por = azar.choice([COBRAR_POR_UNIDAD, COBRAR_POR_CAJA])
                cantidad = azar.randint(1, 120)
                lineas.append({
                    "cantidad": D(cantidad),
                    "precio_unitario": D(azar.randint(1, 99999)) / D(100),
                    "descuento_pct": D("0"),
                    "gravada": azar.random() > 0.2,
                    "unidades_por_caja": unidades,
                    "cobrar_por": cobrar_por,
                })
            totales = calcular_totales(lineas)
            base = totales.base_gravada + totales.base_exenta
            self.assertEqual(totales.subtotal - totales.descuento_total, base)
            self.assertEqual(totales.total, redondear(base + totales.itbms + totales.portes))
            for linea in totales.lineas:
                self.assertEqual(linea.monto, linea.monto.quantize(D("0.01")))
                self.assertGreaterEqual(linea.unidades_por_caja, 1)

    def test_unidades_por_caja_menor_a_uno_se_toma_como_uno(self):
        self.assertEqual(
            monto_linea(D("2"), D("4"), unidades_por_caja=0, cobrar_por=COBRAR_POR_UNIDAD),
            D("8.00"),
        )


class PruebasFormatoDePrecio(SimpleTestCase):
    def test_dos_decimales_minimo(self):
        self.assertEqual(formato_precio(D("30.00")), "30.00")
        self.assertEqual(formato_precio(D("1.25")), "1.25")

    def test_cuatro_decimales_solo_cuando_hace_falta(self):
        self.assertEqual(formato_precio(D("3.333333")), "3.3333")
        self.assertEqual(formato_precio(D("0.5")), "0.50")
        self.assertEqual(formato_precio(D("10")), "10.00")

    def test_recibe_strings_y_decimales(self):
        self.assertEqual(formato_precio("2.3456"), "2.3456")
        self.assertEqual(formato_precio("7"), "7.00")
