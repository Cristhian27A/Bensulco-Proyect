"""Pruebas de la integración de pedidos B2B con facturación."""

from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from catalogo.models import Categoria, ClienteB2B, LineaPedidoB2B, PedidoB2B, Producto
from facturacion.models import Factura, LineaFactura

D = Decimal
User = get_user_model()


class PruebaPedidosPendientes(TestCase):
    """Pruebas de la vista de pedidos pendientes."""

    @classmethod
    def setUpTestData(cls):
        cls.usuario = User.objects.create_user(
            username="vendedor", password="test123"
        )
        cls.cliente = ClienteB2B.objects.create(
            nombre_empresa="Cliente Test S.A.",
            ruc="1-9998888-77-666",
            email_contacto="test@cliente.com",
        )
        cls.categoria = Categoria.objects.create(nombre="Test")
        cls.producto = Producto.objects.create(
            categoria=cls.categoria,
            nombre="Producto Test",
            sku="TEST-001",
            descripcion_corta="Descripción",
            precio_caja=D("10.00"),
            precio_unidad=D("1.00"),
            unidades_por_caja=10,
            aplica_itbms=True,
            estado_activo=True,
        )

    def setUp(self):
        self.client.login(username="vendedor", password="test123")

    def test_la_vista_abre(self):
        respuesta = self.client.get(reverse("facturacion:pedidos_pendientes"))
        self.assertEqual(respuesta.status_code, 200)

    def test_muestra_pedidos_pendientes(self):
        pedido = PedidoB2B.objects.create(
            cliente=self.cliente,
            estado=PedidoB2B.ESTADO_PENDIENTE,
            total_estimado=D("20.00"),
        )
        LineaPedidoB2B.objects.create(
            pedido=pedido,
            producto=self.producto,
            cantidad_cajas=D("2"),
            cantidad_unidades=D("0"),
            subtotal=D("20.00"),
            orden=1,
        )

        respuesta = self.client.get(reverse("facturacion:pedidos_pendientes"))
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, "PED-0001")
        self.assertContains(respuesta, self.cliente.nombre_empresa)


class PruebaDetallePedido(TestCase):
    """Pruebas de la vista de detalle de pedido."""

    @classmethod
    def setUpTestData(cls):
        cls.usuario = User.objects.create_user(
            username="vendedor", password="test123"
        )
        cls.cliente = ClienteB2B.objects.create(
            nombre_empresa="Cliente Test S.A.",
            ruc="1-9998888-77-666",
            email_contacto="test@cliente.com",
        )
        cls.categoria = Categoria.objects.create(nombre="Test")
        cls.producto = Producto.objects.create(
            categoria=cls.categoria,
            nombre="Producto Test",
            sku="TEST-001",
            descripcion_corta="Descripción",
            precio_caja=D("10.00"),
            precio_unidad=D("1.00"),
            unidades_por_caja=10,
            aplica_itbms=True,
            estado_activo=True,
        )
        cls.pedido = PedidoB2B.objects.create(
            cliente=cls.cliente,
            estado=PedidoB2B.ESTADO_PENDIENTE,
            total_estimado=D("20.00"),
            notas="Notas de prueba",
        )
        cls.linea = LineaPedidoB2B.objects.create(
            pedido=cls.pedido,
            producto=cls.producto,
            cantidad_cajas=D("2"),
            cantidad_unidades=D("0"),
            subtotal=D("20.00"),
            orden=1,
        )

    def setUp(self):
        self.client.login(username="vendedor", password="test123")

    def test_el_detalle_abre(self):
        respuesta = self.client.get(
            reverse("facturacion:detalle_pedido", args=[self.pedido.pk])
        )
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, f"PED-{self.pedido.pk:04d}")
        self.assertContains(respuesta, self.cliente.nombre_empresa)
        self.assertContains(respuesta, self.producto.nombre)


class PruebaConversionPedidoAFactura(TestCase):
    """Pruebas de la conversión de pedido a factura."""

    @classmethod
    def setUpTestData(cls):
        cls.usuario = User.objects.create_user(
            username="vendedor", password="test123"
        )
        cls.cliente = ClienteB2B.objects.create(
            nombre_empresa="Cliente Test S.A.",
            ruc="1-9998888-77-666",
            email_contacto="test@cliente.com",
            telefono="+507 0000-0000",
            direccion="Dirección de prueba",
        )
        cls.categoria = Categoria.objects.create(nombre="Test")
        cls.producto = Producto.objects.create(
            categoria=cls.categoria,
            nombre="Producto Test",
            sku="TEST-001",
            descripcion_corta="Descripción",
            precio_caja=D("10.00"),
            precio_unidad=D("1.00"),
            unidades_por_caja=10,
            aplica_itbms=True,
            estado_activo=True,
        )
        cls.pedido = PedidoB2B.objects.create(
            cliente=cls.cliente,
            estado=PedidoB2B.ESTADO_PENDIENTE,
            total_estimado=D("20.00"),
            notas="Notas de prueba",
        )
        cls.linea = LineaPedidoB2B.objects.create(
            pedido=cls.pedido,
            producto=cls.producto,
            cantidad_cajas=D("2"),
            cantidad_unidades=D("0"),
            subtotal=D("20.00"),
            orden=1,
        )

    def setUp(self):
        self.client.login(username="vendedor", password="test123")

    def test_convierte_pedido_a_factura(self):
        respuesta = self.client.post(
            reverse("facturacion:convertir_pedido", args=[self.pedido.pk])
        )
        self.assertEqual(respuesta.status_code, 302)

        # Verificar que se creó la factura
        self.assertEqual(Factura.objects.count(), 1)
        factura = Factura.objects.first()
        self.assertEqual(factura.cliente_nombre, self.cliente.nombre_empresa)
        self.assertEqual(factura.cliente_ruc, self.cliente.ruc)
        self.assertEqual(factura.notas, self.pedido.notas)

        # Verificar que se crearon las líneas
        self.assertEqual(factura.lineas.count(), 1)
        linea_factura = factura.lineas.first()
        self.assertEqual(linea_factura.descripcion, self.producto.nombre)
        self.assertEqual(linea_factura.producto, self.producto)

        # Verificar que el pedido se actualizó
        self.pedido.refresh_from_db()
        self.assertEqual(self.pedido.estado, PedidoB2B.ESTADO_FACTURADO)
        self.assertEqual(self.pedido.factura_generada, factura)

    def test_no_convierte_pedido_facturado(self):
        # Marcar como facturado
        self.pedido.estado = PedidoB2B.ESTADO_FACTURADO
        self.pedido.save()

        respuesta = self.client.post(
            reverse("facturacion:convertir_pedido", args=[self.pedido.pk])
        )
        self.assertEqual(respuesta.status_code, 302)

        # No debería crear nueva factura
        self.assertEqual(Factura.objects.count(), 0)

    def test_no_convierte_pedido_con_factura_generada(self):
        # Crear una factura y asignarla
        from facturacion.services.serie import crear_factura

        factura = crear_factura(
            {
                "fecha": date.today(),
                "cliente_nombre": "Test",
                "itbms_activo": True,
            },
            [],
        )
        self.pedido.factura_generada = factura
        self.pedido.save()

        respuesta = self.client.post(
            reverse("facturacion:convertir_pedido", args=[self.pedido.pk])
        )
        self.assertEqual(respuesta.status_code, 302)

        # No debería crear nueva factura
        self.assertEqual(Factura.objects.count(), 1)
