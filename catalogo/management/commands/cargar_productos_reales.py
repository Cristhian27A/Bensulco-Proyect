"""Carga productos reales de Blixi desde un archivo JSON.

    python manage.py cargar_productos_reales productos.json

El archivo JSON debe tener el siguiente formato:
[
    {
        "categoria": "Bolsas Herméticas",
        "nombre": "Bolsa Hermética 8x10",
        "sku": "BH-001",
        "codigo_barras": "7 595288 003148",
        "descripcion_corta": "Descripción del producto",
        "precio_caja": "45.00",
        "precio_media_caja": "22.50",
        "precio_unidad": "0.75",
        "unidades_por_caja": 60,
        "permite_media_caja": true,
        "aplica_itbms": true,
        "imagen": "ruta/a/imagen.jpg"  // opcional
    },
    ...
]
"""

import json
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from catalogo.models import Categoria, Producto


class Command(BaseCommand):
    help = "Carga productos reales de Blixi desde un archivo JSON."

    def add_arguments(self, parser):
        parser.add_argument(
            "archivo_json",
            type=str,
            help="Ruta al archivo JSON con los productos reales",
        )
        parser.add_argument(
            "--actualizar",
            action="store_true",
            help="Actualiza productos existentes en lugar de crear nuevos",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        archivo_json = options["archivo_json"]
        actualizar = options["actualizar"]

        try:
            with open(archivo_json, "r", encoding="utf-8") as f:
                productos_data = json.load(f)
        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR(f"El archivo {archivo_json} no existe.")
            )
            return
        except json.JSONDecodeError as e:
            self.stdout.write(
                self.style.ERROR(f"Error al leer el JSON: {e}")
            )
            return

        # Crear categorías
        categorias = {}
        for producto in productos_data:
            cat_nombre = producto.get("categoria")
            if cat_nombre and cat_nombre not in categorias:
                categoria, created = Categoria.objects.get_or_create(
                    nombre=cat_nombre
                )
                categorias[cat_nombre] = categoria
                if created:
                    self.stdout.write(f"Categoría creada: {cat_nombre}")

        # Crear o actualizar productos
        for producto_data in productos_data:
            cat_nombre = producto_data.get("categoria")
            sku = producto_data.get("sku")

            if not cat_nombre or not sku:
                self.stdout.write(
                    self.style.WARNING(
                        f"Producto sin categoría o SKU, omitiendo: {producto_data}"
                    )
                )
                continue

            categoria = categorias.get(cat_nombre)
            if not categoria:
                self.stdout.write(
                    self.style.WARNING(
                        f"Categoría no encontrada: {cat_nombre}"
                    )
                )
                continue

            # Preparar datos del producto
            defaults = {
                "categoria": categoria,
                "nombre": producto_data.get("nombre", ""),
                "descripcion_corta": producto_data.get("descripcion_corta", ""),
                "precio_caja": Decimal(str(producto_data.get("precio_caja", "0"))),
                "precio_media_caja": Decimal(str(producto_data.get("precio_media_caja", "0"))) if producto_data.get("precio_media_caja") else None,
                "precio_unidad": Decimal(str(producto_data.get("precio_unidad", "0"))),
                "unidades_por_caja": producto_data.get("unidades_por_caja", 1),
                "permite_media_caja": producto_data.get("permite_media_caja", False),
                "aplica_itbms": producto_data.get("aplica_itbms", True),
                "estado_activo": True,
                "codigo_barras": producto_data.get("codigo_barras", ""),
            }

            if actualizar:
                # Actualizar si existe, crear si no
                producto, created = Producto.objects.update_or_create(
                    sku=sku,
                    defaults=defaults
                )
                if created:
                    self.stdout.write(f"Producto creado: {sku} - {producto_data.get('nombre')}")
                else:
                    self.stdout.write(f"Producto actualizado: {sku} - {producto_data.get('nombre')}")
            else:
                # Solo crear si no existe
                producto, created = Producto.objects.get_or_create(
                    sku=sku,
                    defaults=defaults
                )
                if created:
                    self.stdout.write(f"Producto creado: {sku} - {producto_data.get('nombre')}")
                else:
                    self.stdout.write(f"Producto ya existe (omitido): {sku}")

        self.stdout.write(
            self.style.SUCCESS(
                f"Carga completada:\n"
                f"  {Categoria.objects.count()} categorías\n"
                f"  {Producto.objects.count()} productos"
            )
        )
