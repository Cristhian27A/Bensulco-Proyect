"""Rutas de la app de facturacion."""

from django.urls import path

from facturacion import views

app_name = "facturacion"

urlpatterns = [
    path("", views.nueva_factura, name="nueva"),
    path("historial/", views.historial, name="historial"),
    path("configuracion/", views.configuracion, name="configuracion"),
    path("verificar/<str:serie>/<str:codigo>/", views.verificar, name="verificar"),
    path("factura/<int:pk>/", views.detalle_factura, name="detalle"),
    path("factura/<int:pk>/pdf/", views.factura_pdf, name="pdf"),
    path("factura/<int:pk>/duplicar/", views.duplicar_factura, name="duplicar"),
    path("factura/<int:pk>/anular/", views.anular_factura, name="anular"),
]
