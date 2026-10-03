"""Datos disponibles en todas las plantillas.

La configuracion del negocio (nombre, RUC, color) se usa en la cabecera de
todas las pantallas, asi que se injecta una sola vez desde aqui en vez de
repasarla en cada vista.
"""

from facturacion.models import ConfiguracionNegocio


def configuracion_negocio(request):
    return {"configuracion": ConfiguracionNegocio.cargar()}
