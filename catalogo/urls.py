"""Rutas de la app de catálogo."""

from django.urls import path

from catalogo import views

app_name = "catalogo"

urlpatterns = [
    path("", views.catalogo_publico, name="catalogo"),
    path("agregar/", views.agregar_al_carrito, name="agregar"),
    path("eliminar/<int:producto_id>/", views.eliminar_del_carrito, name="eliminar"),
    path("vaciar/", views.vaciar_carrito, name="vaciar"),
    path("pedido/", views.formulario_pedido, name="formulario_pedido"),
    path("pedido/exitoso/<int:pedido_id>/", views.pedido_exitoso, name="pedido_exitoso"),
    path("pedido/<int:pedido_id>/pdf/", views.pdf_pedido, name="pdf_pedido"),
    path("api/buscar-productos/", views.api_buscar_productos, name="api_buscar_productos"),
]
