"""Rutas de la app de facturacion."""

from django.urls import path

from facturacion import views

app_name = "facturacion"

urlpatterns = [
    path("", views.nueva_factura, name="nueva"),
    path("historial/", views.historial, name="historial"),
    path("configuracion/", views.configuracion, name="configuracion"),
    path("verificar/<str:serie>/<str:codigo>/", views.verificar, name="verificar"),
    path("pedidos/", views.pedidos_pendientes, name="pedidos_pendientes"),
    path("pedidos/<int:pedido_id>/", views.detalle_pedido, name="detalle_pedido"),
    path("pedidos/<int:pedido_id>/convertir/", views.convertir_pedido_a_factura, name="convertir_pedido"),
    path("factura/<int:pk>/", views.detalle_factura, name="detalle"),
    path("factura/<int:pk>/pdf/", views.factura_pdf, name="pdf"),
    path("factura/<int:pk>/duplicar/", views.duplicar_factura, name="duplicar"),
    path("factura/<int:pk>/anular/", views.anular_factura, name="anular"),
    path("factura/<int:pk>/eliminar/confirmar/", views.confirmar_eliminar_factura, name="confirmar_eliminar"),
    path("factura/<int:pk>/eliminar/", views.eliminar_factura, name="eliminar"),
]
