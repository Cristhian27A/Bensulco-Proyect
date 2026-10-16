"""Configuracion del proyecto de facturacion."""

import os
from pathlib import Path

from decouple import Config, Csv, RepositoryEnv

BASE_DIR = Path(__file__).resolve().parent.parent

# El archivo .env se lee SOLO de la carpeta del proyecto (RepositoryEnv no sube
# por el arbol), para que el resultado no dependa de otros .env del equipo.
config = Config(RepositoryEnv(str(BASE_DIR / ".env")))

SECRET_KEY = config(
    "SECRET_KEY",
    default="clave-de-desarrollo-cambiala-en-produccion-9f3a1c7e5b2d8a4f",
)

DEBUG = config("DEBUG", default=True, cast=bool)

ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="*", cast=Csv())

CSRF_TRUSTED_ORIGINS = config("CSRF_TRUSTED_ORIGINS", default="", cast=Csv())

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "facturacion",
    "catalogo",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "facturas.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "facturacion.context_processors.configuracion_negocio",
            ],
        },
    },
]

WSGI_APPLICATION = "facturas.wsgi.application"

# Se usa MySQL cuando hay credenciales en el archivo .env.
# Si no las hay, se cae a SQLite para poder correr los tests en cualquier maquina.
_USAR_SQLITE = config("USAR_SQLITE", default=False, cast=bool)
_SIN_CREDENCIALES = not (
    config("DB_NAME", default="") and config("DB_USER", default="")
)

if _USAR_SQLITE or _SIN_CREDENCIALES:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": config("DB_NAME"),
            "USER": config("DB_USER"),
            "PASSWORD": config("DB_PASSWORD", default=""),
            "HOST": config("DB_HOST", default="127.0.0.1"),
            "PORT": config("DB_PORT", default="3306"),
            "OPTIONS": {
                "charset": "utf8mb4",
            },
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "es-pa"
TIME_ZONE = "America/Panama"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "facturacion" / "static"]

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "facturacion" / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Numero de decimales usados en toda la facturacion.
FACTURA_DECIMALES = 2

# Valor predeterminado de la empresa en el PDF (se puede cambiar en Configuracion).
FACTURA_COLOR_PREDETERMINADA = "#3A0088"

# Configuracion de autenticacion
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "facturacion:nueva"
LOGOUT_REDIRECT_URL = "login"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"consola": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["consola"], "level": "INFO"},
}

os.makedirs(MEDIA_ROOT, exist_ok=True)
