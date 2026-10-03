"""Utilidades para inspeccionar el PDF generado en las pruebas.

Permiten contar páginas, extraer el texto de cada página y obtener la
posición de cada fragmento de texto. Sirven para comprobar de verdad que
los totales y las firmas quedan juntos en la última página y que ningún
texto se sale de los márgenes ni se monta con otro.
"""

import base64
import re
import zlib
from math import atan2, cos, degrees, radians, sin

from reportlab.pdfbase.pdfmetrics import stringWidth

# Un texto dibujado: (x, y, texto, fuente, tamaño)
Fragmento = tuple


def _objetos(datos: bytes) -> dict:
    """Divide el PDF en sus objetos indirectos."""
    objetos = {}
    for coincidencia in re.finditer(rb"(\d+)\s+0\s+obj\b(.*?)\bendobj", datos, re.S):
        objetos[int(coincidencia.group(1))] = coincidencia.group(2)
    return objetos


def _flujo(cuerpo: bytes) -> bytes:
    """Devuelve el contenido descomprimido de un objeto stream.

    ReportLab escribe los flujos como ASCII85 y luego comprimidos, así que
    se deshacen los dos filtros.
    """
    coincidencia = re.search(rb"stream\r?\n(.*?)\r?\n?endstream", cuerpo, re.S)
    if not coincidencia:
        return b""
    datos = coincidencia.group(1)
    if b"/ASCII85Decode" in cuerpo:
        limpio = datos.strip()
        if limpio.startswith(b"<~"):
            limpio = limpio[2:]
        if limpio.endswith(b"~>"):
            limpio = limpio[:-2]
        try:
            datos = base64.a85decode(limpio)
        except ValueError:
            return b""
    if b"/FlateDecode" in cuerpo:
        try:
            datos = zlib.decompress(datos)
        except zlib.error:
            return b""
    return datos


def _paginas_en_orden(objetos: dict) -> list:
    """Lista los números de objeto de las páginas, en orden de lectura."""
    raiz = None
    for cuerpo in objetos.values():
        if b"/Type /Pages" in cuerpo and b"/Kids" in cuerpo:
            raiz = cuerpo
            break
    if raiz is None:
        return []
    hijos = re.search(rb"/Kids\s*\[(.*?)\]", raiz, re.S)
    if not hijos:
        return []
    return [int(n) for n in re.findall(rb"(\d+)\s+0\s+R", hijos.group(1))]


def numero_de_paginas(datos: bytes) -> int:
    """Cuenta las páginas del PDF."""
    objetos = _objetos(datos)
    paginas = _paginas_en_orden(objetos)
    if paginas:
        return len(paginas)
    return len(re.findall(rb"/Type\s*/Page[^s]", datos))


def _contenido_de_pagina(objetos: dict, numero: int) -> bytes:
    """Devuelve el flujo de contenido de una página."""
    cuerpo = objetos.get(numero, b"")
    referencia = re.search(rb"/Contents\s+(\d+)\s+0\s+R", cuerpo)
    if referencia:
        return _flujo(objetos.get(int(referencia.group(1)), b""))
    lista = re.search(rb"/Contents\s*\[(.*?)\]", cuerpo, re.S)
    if lista:
        partes = []
        for n in re.findall(rb"(\d+)\s+0\s+R", lista.group(1)):
            partes.append(_flujo(objetos.get(int(n), b"")))
        return b"".join(partes)
    return b""


# Cadena literal de PDF: admite escapes y paréntesis dentro.
_CADENA = re.compile(rb"\((?:\\.|[^()\\])*\)", re.S)


ESCAPES = {
    b"n": b"\n", b"r": b"\r", b"t": b"\t", b"b": b"\b",
    b"f": b"\f", b"(": b"(", b")": b")", b"\\": b"\\",
}


def _descifrar(bruto: bytes) -> str:
    """Convierte una cadena literal de PDF a texto.

    ReportLab escribe los acentos como escapes octales en WinAnsi, por eso
    se reconstruyen los bytes y se leen con esa codificación.
    """
    texto = bruto[1:-1]
    salida = bytearray()
    i = 0
    while i < len(texto):
        caracter = texto[i:i + 1]
        if caracter != b"\\" or i + 1 >= len(texto):
            salida += caracter
            i += 1
            continue
        siguiente = texto[i + 1:i + 2]
        if siguiente.isdigit():
            j = i + 1
            digitos = b""
            while j < len(texto) and len(digitos) < 3 and texto[j:j + 1].isdigit():
                digitos += texto[j:j + 1]
                j += 1
            salida.append(int(digitos, 8) & 0xFF)
            i = j
            continue
        salida += ESCAPES.get(siguiente, siguiente)
        i += 2
    return salida.decode("cp1252", errors="replace")


def texto_de_pagina(datos: bytes, indice: int = 0) -> str:
    """Texto visible de una página (0 es la primera)."""
    objetos = _objetos(datos)
    paginas = _paginas_en_orden(objetos)
    if indice >= len(paginas):
        return ""
    flujo = _contenido_de_pagina(objetos, paginas[indice])
    partes = [_descifrar(c) for c in _CADENA.findall(flujo)]
    return " ".join(p for p in partes if p.strip())


def textos_por_pagina(datos: bytes) -> list:
    """Lista con el texto de cada página."""
    objetos = _objetos(datos)
    paginas = _paginas_en_orden(objetos)
    return [texto_de_pagina(datos, i) for i in range(len(paginas))]


# Fuentes de ReportLab: nombre PostScript interno -> nombre de la fuente.
FUENTES = {
    "F1": "Helvetica",
    "F2": "Helvetica-Bold",
    "F3": "Helvetica-Oblique",
    "F4": "Helvetica-BoldOblique",
    "F5": "Courier",
    "F6": "Courier-Bold",
    "F7": "Courier-Oblique",
    "F8": "Courier-BoldOblique",
    "F9": "Symbol",
    "F10": "ZapfDingbats",
}


def _multiplicar(una, otra):
    """Multiplica dos matrices de transformación [a b c d e f]."""
    a1, b1, c1, d1, e1, f1 = una
    a2, b2, c2, d2, e2, f2 =otra
    return [
        a1 * a2 + b1 * c2,
        a1 * b2 + b1 * d2,
        c1 * a2 + d1 * c2,
        c1 * b2 + d1 * d2,
        e1 * a2 + f1 * c2 + e2,
        e1 * b2 + f1 * d2 + f2,
    ]


IDENTIDAD = [1.0, 0.0, 0.0, 1.0, 0.0, 0.0]


def _transformar(matriz, x, y):
    a, b, c, d, e, f = matriz
    return a * x + c * y + e, b * x + d * y + f


def _fragmentos_tj(interior: bytes, x, y, tamano, fuente) -> list:
    """Parte un arreglo TJ en fragmentos, respetando el desplazamiento.

    ReportLab escribe una linea con varios tipos de letra como un arreglo TJ
    con numeros de ajuste entre los textos. Sin tomarlos en cuenta, todas las
    partes de la linea saldrian en la misma x y parecerian montadas.
    """
    elementos = re.finditer(
        rb"\((?P<txt>(?:\\.|[^()\\])*)\)|(?P<num>-?[\d.]+)", interior
    )
    fragmentos = []
    desplazamiento = 0.0
    for elemento in elementos:
        if elemento.group("txt") is not None:
            texto = _descifrar(b"(" + elemento.group("txt") + b")")
            if texto.strip():
                fragmentos.append((
                    x + desplazamiento, y, texto, fuente, tamano, 0.0
                ))
        else:
            # El numero se resta: es el ajuste que se aplica al texto que sigue.
            desplazamiento -= float(elemento.group("num")) / 1000.0 * tamano
    return fragmentos


def fragmentos_de_pagina(datos: bytes, indice: int = 0) -> list:
    """Devuelve (x, y, texto, fuente, tamaño, ángulo) de cada texto de una página.

    Sigue la matriz de texto (Tm), los desplazamientos (Td/TD) y la matriz
    vigente del lienzo (cm), que es lo que Platypus usa para dibujar cada
    línea. El ángulo sirve para detectar el texto girado, como la marca de
    agua de una factura anulada.
    """
    objetos = _objetos(datos)
    paginas = _paginas_en_orden(objetos)
    if indice >= len(paginas):
        return []

    flujo = _contenido_de_pagina(objetos, paginas[indice])

    # Se recorren los operadores de a uno en uno, en orden.
    patron = re.compile(
        rb"(?P<tf>/(?P<fuente>\w+)\s+(?P<tamano>[\d.]+)\s+Tf)"
        rb"|(?P<tm>(?P<tmx>-?[\d.]+)\s+(?P<tmy>-?[\d.]+)\s+(?P<tmtx>-?[\d.]+)\s+"
        rb"(?P<tmyy>-?[\d.]+)\s+(?P<tmxx>-?[\d.]+)\s+(?P<tmyy2>-?[\d.]+)\s+Tm)"
        rb"|(?P<td>(?P<tdx>-?[\d.]+)\s+(?P<tdy>-?[\d.]+)\s+T[dD])"
        rb"|(?P<cm>(?P<cmx>-?[\d.]+)\s+(?P<cmy>-?[\d.]+)\s+(?P<cmxx>-?[\d.]+)\s+"
        rb"(?P<cmyy>-?[\d.]+)\s+(?P<cmex>-?[\d.]+)\s+(?P<cmey>-?[\d.]+)\s+cm)"
        rb"|(?P<qq>\bq\b)"
        rb"|(?P<qqfin>\bQ\b)"
        rb"|(?P<tl>(?P<tlvalor>-?[\d.]+)\s+TL)"
        rb"|(?P<tasterisco>\bT\*)"
        rb"|(?P<tj>\((?P<txt>(?:\\.|[^()\\])*)\)\s*Tj)"
        rb"|(?P<tj2>\[(?P<txt2>[^\]]*)\]\s*TJ)",
        re.S,
    )

    fragmentos = []
    fuente_actual = "F1"
    tamano_actual = 10.0
    matriz_texto = IDENTIDAD
    matriz_lienzo = IDENTIDAD
    pila = []
    interlineado = 0.0
    x_linea, y_linea = 0.0, 0.0
    inicio_linea = 0.0

    for coincidencia in patron.finditer(flujo):
        grupos = coincidencia.groupdict()
        if grupos["tf"]:
            fuente_actual = grupos["fuente"].decode("ascii")
            tamano_actual = float(grupos["tamano"])
        elif grupos["tm"]:
            # "a b c d e f Tm": la posición es e,f y la rotación a,b,c,d.
            matriz_texto = [
                float(grupos["tmx"]), float(grupos["tmy"]),
                float(grupos["tmtx"]), float(grupos["tmyy"]),
                float(grupos["tmxx"]), float(grupos["tmyy2"]),
            ]
            x_linea, y_linea = matriz_texto[4], matriz_texto[5]
            inicio_linea = x_linea
        elif grupos["td"]:
            # "x y Td" mueve la línea base sin cambiar la matriz.
            matriz_texto = [
                matriz_texto[0], matriz_texto[1], matriz_texto[2], matriz_texto[3],
                matriz_texto[4] + float(grupos["tdx"]),
                matriz_texto[5] + float(grupos["tdy"]),
            ]
            x_linea, y_linea = matriz_texto[4], matriz_texto[5]
        elif grupos["cm"]:
            # "a b c d e f cm" multiplica por la izquierda: M x CTM.
            matriz_lienzo = _multiplicar([
                float(grupos["cmx"]), float(grupos["cmy"]),
                float(grupos["cmxx"]), float(grupos["cmyy"]),
                float(grupos["cmex"]), float(grupos["cmey"]),
            ], matriz_lienzo)
        elif grupos["tl"]:
            interlineado = float(grupos["tlvalor"])
        elif grupos["tasterisco"]:
            # T* baja una linea y vuelve al principio de la anterior: el
            # avance que dejaran los textos de la linea no se hereda.
            matriz_texto = [
                matriz_texto[0], matriz_texto[1], matriz_texto[2], matriz_texto[3],
                inicio_linea, matriz_texto[5] - interlineado,
            ]
            x_linea, y_linea = inicio_linea, matriz_texto[5]
        elif grupos["qq"]:
            pila.append(list(matriz_lienzo))
        elif grupos["qqfin"]:
            if pila:
                matriz_lienzo = pila.pop()
        else:
            completa = _multiplicar(matriz_texto, matriz_lienzo)
            x_actual, y_actual = completa[4], completa[5]
            angulo = degrees(atan2(completa[1], completa[0]))
            if grupos["tj"] is not None:
                texto = _descifrar(b"(" + grupos["txt"] + b")")
                if texto.strip():
                    fragmentos.append(
                        (x_actual, y_actual, texto, fuente_actual,
                         tamano_actual, angulo)
                    )
                # Tras un Tj el siguiente texto sigue justo despues, sin
                # que ReportLab vuelva a posicionar la linea base.
                matriz_texto[4] += stringWidth(
                    texto, FUENTES.get(fuente_actual, "Helvetica"), tamano_actual
                )
            else:
                # En un arreglo TJ cada texto lleva su propio desplazamiento.
                for parcial in _fragmentos_tj(
                    grupos["txt2"] or b"", x_actual, y_actual,
                    tamano_actual, fuente_actual,
                ):
                    xo, yo, texto, fuente, tamano, _ang = parcial
                    if angulo:
                        xo, yo = _transformar(completa, xo - x_actual, yo - y_actual)
                    fragmentos.append(
                        (xo, yo, texto, fuente, tamano, angulo)
                    )
    return fragmentos


def cajas(fragmentos: list) -> list:
    """Convierte fragmentos en cajas (x0, y0, x1, y1, texto).

    Si el texto está girado se toma la caja que lo rodea, girada igual.
    """
    resultado = []
    for x, y, texto, fuente, tamano, angulo in fragmentos:
        nombre = FUENTES.get(fuente, "Helvetica")
        ancho = stringWidth(texto, nombre, tamano)
        # El origen del texto es la línea base: la caja sube un poco el texto.
        puntos = [
            (0, -tamano * 0.25), (ancho, -tamano * 0.25),
            (0, tamano * 0.80), (ancho, tamano * 0.80),
        ]
        if abs(angulo) > 0.5:
            radianes = radians(angulo)
            seno, coseno = sin(radianes), cos(radianes)
            girados = [
                (x + px * coseno - py * seno, y + px * seno + py * coseno)
                for px, py in puntos
            ]
        else:
            girados = [(x + px, y + py) for px, py in puntos]
        resultado.append((
            min(p[0] for p in girados), min(p[1] for p in girados),
            max(p[0] for p in girados), max(p[1] for p in girados),
            texto,
        ))
    return resultado


def es_decorativo(fragmento) -> bool:
    """El texto grande y girado es la marca de agua, no un dato de la factura."""
    return abs(fragmento[5]) > 5.0


def texto_normal(fragmentos: list) -> list:
    """Quita la marca de agua para poder medir márgenes y solapes."""
    return [f for f in fragmentos if not es_decorativo(f)]


def solapan(uno, otro) -> bool:
    """¿Las dos cajas se pisan? Tolera un margen pequeño por redondeos."""
    margen = 0.6
    return (
        uno[0] < otro[2] - margen
        and otro[0] < uno[2] - margen
        and uno[1] < otro[3] - margen
        and otro[1] < uno[3] - margen
    )


def solapamientos(datos: bytes, indice: int = 0) -> list:
    """Pares de textos que se montan entre sí en una página.

    La marca de agua va aparte y de fondo, así que no cuenta.
    """
    cajas_pagina = cajas(texto_normal(fragmentos_de_pagina(datos, indice)))
    encontrados = []
    for i in range(len(cajas_pagina)):
        for j in range(i + 1, len(cajas_pagina)):
            if solapan(cajas_pagina[i], cajas_pagina[j]):
                encontrados.append((cajas_pagina[i], cajas_pagina[j]))
    return encontrados
