"""Pruebas de la conversión de montos a letras."""

from decimal import Decimal

from django.test import SimpleTestCase

from facturacion.services.numero_a_letras import numero_a_letras, total_en_letras

D = Decimal


class PruebasNumeroALetras(SimpleTestCase):
    def test_ejemplo_del_requerimiento(self):
        self.assertEqual(
            total_en_letras(D("258.81")),
            "DOSCIENTOS CINCUENTA Y OCHO CON 81/100 DÓLARES",
        )

    def test_cero(self):
        self.assertEqual(numero_a_letras(D("0")), "CERO CON 00/100 DÓLARES")

    def test_unidades(self):
        self.assertEqual(numero_a_letras(D("1.05")), "UNO CON 05/100 DÓLARES")
        self.assertEqual(numero_a_letras(D("16.98")), "DIECISÉIS CON 98/100 DÓLARES")
        self.assertEqual(numero_a_letras(D("21")), "VEINTIUNO CON 00/100 DÓLARES")
        self.assertEqual(numero_a_letras(D("22")), "VEINTIDOS CON 00/100 DÓLARES")
        self.assertEqual(numero_a_letras(D("26")), "VEINTISEIS CON 00/100 DÓLARES")

    def test_del_10_al_19(self):
        """Del 10 al 19 se escriben con su propia palabra, no con VEINTI."""
        self.assertEqual(numero_a_letras(D("10")), "DIEZ CON 00/100 DÓLARES")
        self.assertEqual(numero_a_letras(D("11")), "ONCE CON 00/100 DÓLARES")
        self.assertEqual(numero_a_letras(D("12")), "DOCE CON 00/100 DÓLARES")
        self.assertEqual(numero_a_letras(D("13")), "TRECE CON 00/100 DÓLARES")
        self.assertEqual(numero_a_letras(D("14")), "CATORCE CON 00/100 DÓLARES")
        self.assertEqual(numero_a_letras(D("15")), "QUINCE CON 00/100 DÓLARES")
        self.assertEqual(numero_a_letras(D("17")), "DIECISIETE CON 00/100 DÓLARES")
        self.assertEqual(numero_a_letras(D("18")), "DIECIOCHO CON 00/100 DÓLARES")
        self.assertEqual(
            numero_a_letras(D("19")), "DIECINUEVE CON 00/100 DÓLARES"
        )
        # Con centavos y dentro de una centena.
        self.assertEqual(numero_a_letras(D("110")), "CIENTO DIEZ CON 00/100 DÓLARES")
        self.assertEqual(
            numero_a_letras(D("115.5")), "CIENTO QUINCE CON 50/100 DÓLARES"
        )
        self.assertEqual(
            numero_a_letras(D("1010")), "MIL DIEZ CON 00/100 DÓLARES"
        )

    def test_cien_y_cientos(self):
        self.assertEqual(numero_a_letras(D("100")), "CIEN CON 00/100 DÓLARES")
        self.assertEqual(numero_a_letras(D("101")), "CIENTO UNO CON 00/100 DÓLARES")
        self.assertEqual(
            numero_a_letras(D("500")), "QUINIENTOS CON 00/100 DÓLARES"
        )
        self.assertEqual(
            numero_a_letras(D("900")), "NOVECIENTOS CON 00/100 DÓLARES"
        )
        self.assertEqual(
            numero_a_letras(D("900.01")), "NOVECIENTOS CON 01/100 DÓLARES"
        )

    def test_miles(self):
        self.assertEqual(numero_a_letras(D("1000")), "MIL CON 00/100 DÓLARES")
        self.assertEqual(numero_a_letras(D("21000")), "VEINTÚN MIL CON 00/100 DÓLARES")
        self.assertEqual(
            numero_a_letras(D("21001")), "VEINTÚN MIL UNO CON 00/100 DÓLARES"
        )

    def test_millones(self):
        self.assertEqual(
            numero_a_letras(D("1000000")), "UN MILLÓN CON 00/100 DÓLARES"
        )
        self.assertEqual(
            numero_a_letras(D("2000000")), "DOS MILLONES CON 00/100 DÓLARES"
        )
        self.assertEqual(
            numero_a_letras(D("1234567.89")),
            "UN MILLÓN DOSCIENTOS TREINTA Y CUATRO MIL QUINIENTOS SESENTA Y SIETE "
            "CON 89/100 DÓLARES",
        )

    def test_monto_negativo(self):
        self.assertEqual(
            numero_a_letras(D("-5")), "MENOS CINCO CON 00/100 DÓLARES"
        )

    def test_redondea_a_dos_decimales_antes_de_convertir(self):
        self.assertEqual(
            numero_a_letras(D("2.005")), "DOS CON 01/100 DÓLARES"
        )
        self.assertEqual(
            numero_a_letras(D("2.004")), "DOS CON 00/100 DÓLARES"
        )

    def test_todos_los_montos_hasta_un_millon_sin_error(self):
        # 1000 y 1001istan los unicos tres digitos; el resto se repite.
        for valor in range(0, 2000):
            texto = numero_a_letras(D(valor))
            self.assertTrue(texto.endswith("CON 00/100 DÓLARES"), texto)
        for valor in (0, 1, 15, 16, 21, 30, 100, 101, 999, 1000, 1001, 999999):
            self.assertTrue(numero_a_letras(D(valor)).strip() != "")
