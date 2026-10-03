"""Conversión de montos a letras en español.

Uso típico:

    >>> total_en_letras(Decimal("258.81"))
    'DOSCIENTOS CINCUENTA Y OCHO CON 81/100 DÓLARES'

La palabra "UN" se apocopa antes de "mil" y "millón" (veintiún mil,
veintiún millones). Sin apocopa queda "UNO", que es lo correcto cuando
el monto va solo (uno con 50/100) o cuando la palabra siguiente es femenina.
"""

from decimal import Decimal, ROUND_HALF_UP

CERO = Decimal("0.00")
MONEDA = "DÓLARES"

UNIDADES = [
    "", "UNO", "DOS", "TRES", "CUATRO", "CINCO", "SEIS", "SIETE", "OCHO", "NUEVE",
    "DIEZ", "ONCE", "DOCE", "TRECE", "CATORCE", "QUINCE",
    "DIECISÉIS", "DIECISIETE", "DIECIOCHO", "DIECINUEVE",
    "VEINTE",
]

DECENAS = [
    "", "", "VEINTI",
    "TREINTA", "CUARENTA", "CINCUENTA", "SESENTA", "SETENTA",
    "OCHENTA", "NOVENTA",
]

CENTENAS = [
    "", "CIENTO", "DOSCIENTOS", "TRESCIENTOS", "CUATROCIENTOS",
    "QUINIENTOS", "SEISCIENTOS", "SETECIENTOS", "OCHOCIENTOS", "NOVECIENTOS",
]

# Millón, mil millones, mil. Se usan de mayor a menor.
ESCALA = [
    (10 ** 12, "BILLÓN", "BILLONES"),
    (10 ** 9, "MIL MILLONES", "MIL MILLONES"),
    (10 ** 6, "MILLÓN", "MILLONES"),
    (10 ** 3, "MIL", "MIL"),
]


def _tres_digitos(numero: int) -> str:
    """Convierte un número de 0 a 999 a letras."""
    if numero <= 0:
        return ""
    if numero == 100:
        return "CIEN"

    partes = []
    centena, resto = divmod(numero, 100)
    if centena:
        partes.append(CENTENAS[centena])

    if resto == 0:
        return " ".join(partes)

    if resto < 30:
        if resto <= 19:
            # 1 a 19: uno, diez, once, dieciseis, diecinueve.
            partes.append(UNIDADES[resto])
        else:
            # 20 a 29: veinte, veintiuno, veintidos...
            partes.append("VEINTI" + UNIDADES[resto - 20])
    else:
        decena, unidad = divmod(resto, 10)
        base = DECENAS[decena]
        partes.append(f"{base} Y {UNIDADES[unidad]}" if unidad else base)

    return " ".join(partes).strip()


def _apocopar(texto: str) -> str:
    """Cambia UNO por UN y VEINTIUNO por VEINTÚN antes de mil / millón."""
    palabras = texto.split()
    if not palabras:
        return texto
    ultima = palabras[-1]
    if ultima == "UNO":
        palabras[-1] = "UN"
    elif ultima == "VEINTIUNO":
        palabras[-1] = "VEINTÚN"
    return " ".join(palabras)


def _hasta_millares(numero: int) -> str:
    """Letras de un número entre 1 y 999999, agrupando los miles."""
    miles, resto = divmod(numero, 1000)
    partes = []
    if miles:
        partes.append("MIL" if miles == 1 else f"{_apocopar(_tres_digitos(miles))} MIL")
    if resto:
        partes.append(_tres_digitos(resto))
    return " ".join(partes).strip()


def _entero_a_letras(numero: int) -> str:
    """Convierte un entero no negativo a letras en mayúsculas."""
    if numero < 0:
        return "MENOS " + _entero_a_letras(abs(numero))
    if numero == 0:
        return "CERO"

    resto = numero
    partes = []
    for factor, singular, plural in ESCALA:
        valor, resto = divmod(resto, factor)
        if valor == 0:
            continue
        if factor == 10 ** 3:
            partes.append("MIL" if valor == 1 else f"{_apocopar(_hasta_millares(valor))} MIL")
        else:
            nombre = singular if valor == 1 else plural
            if valor == 1:
                partes.append(f"UN {nombre}")
            else:
                partes.append(f"{_apocopar(_hasta_millares(valor))} {nombre}")

    if resto:
        partes.append(_hasta_millares(resto))
    return " ".join(partes).strip()


def numero_a_letras(numero, moneda=MONEDA, con_decimales=True) -> str:
    """Devuelve el monto escrito en palabras, en mayúsculas.

    >>> numero_a_letras(Decimal("1.05"))
    'UNO CON 05/100 DÓLARES'
    """
    valor = Decimal(str(numero)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    entero = int(valor)
    centimos = int((valor - entero) * 100)

    texto = _entero_a_letras(entero)
    if con_decimales:
        texto = f"{texto} CON {centimos:02d}/100"
    if moneda:
        texto = f"{texto} {moneda}"
    return texto


def total_en_letras(total, moneda=MONEDA) -> str:
    """Alias usado por el modelo Factura."""
    return numero_a_letras(total, moneda=moneda)
