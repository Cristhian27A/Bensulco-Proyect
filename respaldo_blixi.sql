-- MySQL dump 10.13  Distrib 8.0.46, for Win64 (x86_64)
--
-- Host: localhost    Database: facturas
-- ------------------------------------------------------
-- Server version	8.0.46

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group`
--

LOCK TABLES `auth_group` WRITE;
/*!40000 ALTER TABLE `auth_group` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group_permissions`
--

DROP TABLE IF EXISTS `auth_group_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `group_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group_permissions`
--

LOCK TABLES `auth_group_permissions` WRITE;
/*!40000 ALTER TABLE `auth_group_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_permission` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `content_type_id` int NOT NULL,
  `codename` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=65 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_permission`
--

LOCK TABLES `auth_permission` WRITE;
/*!40000 ALTER TABLE `auth_permission` DISABLE KEYS */;
INSERT INTO `auth_permission` VALUES (1,'Can add log entry',1,'add_logentry'),(2,'Can change log entry',1,'change_logentry'),(3,'Can delete log entry',1,'delete_logentry'),(4,'Can view log entry',1,'view_logentry'),(5,'Can add permission',2,'add_permission'),(6,'Can change permission',2,'change_permission'),(7,'Can delete permission',2,'delete_permission'),(8,'Can view permission',2,'view_permission'),(9,'Can add group',3,'add_group'),(10,'Can change group',3,'change_group'),(11,'Can delete group',3,'delete_group'),(12,'Can view group',3,'view_group'),(13,'Can add user',4,'add_user'),(14,'Can change user',4,'change_user'),(15,'Can delete user',4,'delete_user'),(16,'Can view user',4,'view_user'),(17,'Can add content type',5,'add_contenttype'),(18,'Can change content type',5,'change_contenttype'),(19,'Can delete content type',5,'delete_contenttype'),(20,'Can view content type',5,'view_contenttype'),(21,'Can add session',6,'add_session'),(22,'Can change session',6,'change_session'),(23,'Can delete session',6,'delete_session'),(24,'Can view session',6,'view_session'),(25,'Can add Configuracion del negocio',7,'add_configuracionnegocio'),(26,'Can change Configuracion del negocio',7,'change_configuracionnegocio'),(27,'Can delete Configuracion del negocio',7,'delete_configuracionnegocio'),(28,'Can view Configuracion del negocio',7,'view_configuracionnegocio'),(29,'Can add Contador de serie',8,'add_contadorserie'),(30,'Can change Contador de serie',8,'change_contadorserie'),(31,'Can delete Contador de serie',8,'delete_contadorserie'),(32,'Can view Contador de serie',8,'view_contadorserie'),(33,'Can add Factura',9,'add_factura'),(34,'Can change Factura',9,'change_factura'),(35,'Can delete Factura',9,'delete_factura'),(36,'Can view Factura',9,'view_factura'),(37,'Can add Linea de factura',10,'add_lineafactura'),(38,'Can change Linea de factura',10,'change_lineafactura'),(39,'Can delete Linea de factura',10,'delete_lineafactura'),(40,'Can view Linea de factura',10,'view_lineafactura'),(41,'Can add Contador de orden de compra',11,'add_contadorordencompra'),(42,'Can change Contador de orden de compra',11,'change_contadorordencompra'),(43,'Can delete Contador de orden de compra',11,'delete_contadorordencompra'),(44,'Can view Contador de orden de compra',11,'view_contadorordencompra'),(45,'Can add Pedido B2B',12,'add_pedidob2b'),(46,'Can change Pedido B2B',12,'change_pedidob2b'),(47,'Can delete Pedido B2B',12,'delete_pedidob2b'),(48,'Can view Pedido B2B',12,'view_pedidob2b'),(49,'Can add Cliente B2B',13,'add_clienteb2b'),(50,'Can change Cliente B2B',13,'change_clienteb2b'),(51,'Can delete Cliente B2B',13,'delete_clienteb2b'),(52,'Can view Cliente B2B',13,'view_clienteb2b'),(53,'Can add Línea de pedido B2B',14,'add_lineapedidob2b'),(54,'Can change Línea de pedido B2B',14,'change_lineapedidob2b'),(55,'Can delete Línea de pedido B2B',14,'delete_lineapedidob2b'),(56,'Can view Línea de pedido B2B',14,'view_lineapedidob2b'),(57,'Can add Producto',15,'add_producto'),(58,'Can change Producto',15,'change_producto'),(59,'Can delete Producto',15,'delete_producto'),(60,'Can view Producto',15,'view_producto'),(61,'Can add Categoría',16,'add_categoria'),(62,'Can change Categoría',16,'change_categoria'),(63,'Can delete Categoría',16,'delete_categoria'),(64,'Can view Categoría',16,'view_categoria');
/*!40000 ALTER TABLE `auth_permission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user`
--

DROP TABLE IF EXISTS `auth_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_user` (
  `id` int NOT NULL AUTO_INCREMENT,
  `password` varchar(128) COLLATE utf8mb4_unicode_ci NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `first_name` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `last_name` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(254) COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user`
--

LOCK TABLES `auth_user` WRITE;
/*!40000 ALTER TABLE `auth_user` DISABLE KEYS */;
INSERT INTO `auth_user` VALUES (1,'pbkdf2_sha256$1000000$ycBBb3r2OLiBPnuZlZwneh$jXkW0X4IPCWZwi8Zv1H2a1x9djESwK/quXfqziXbyac=',NULL,1,'cristhianAdmin','','','',1,1,'2026-10-04 16:19:13.019483'),(2,'pbkdf2_sha256$1000000$7c6TijJrpO2pce5xfhgogl$uyFJ1H8+i2ovOOt/So3TjFk+zUX8c8LMq/DHmdPzdxc=','2026-10-19 00:23:15.125598',1,'admin','','','admin@ejemplo.com',1,1,'2026-10-04 17:10:11.973428');
/*!40000 ALTER TABLE `auth_user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user_groups`
--

DROP TABLE IF EXISTS `auth_user_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_user_groups` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `group_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_groups_user_id_group_id_94350c0c_uniq` (`user_id`,`group_id`),
  KEY `auth_user_groups_group_id_97559544_fk_auth_group_id` (`group_id`),
  CONSTRAINT `auth_user_groups_group_id_97559544_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `auth_user_groups_user_id_6a12ed8b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_groups`
--

LOCK TABLES `auth_user_groups` WRITE;
/*!40000 ALTER TABLE `auth_user_groups` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user_user_permissions`
--

DROP TABLE IF EXISTS `auth_user_user_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_user_user_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_user_permissions_user_id_permission_id_14a6b632_uniq` (`user_id`,`permission_id`),
  KEY `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_user_permissions`
--

LOCK TABLES `auth_user_user_permissions` WRITE;
/*!40000 ALTER TABLE `auth_user_user_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user_user_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `catalogo_categoria`
--

DROP TABLE IF EXISTS `catalogo_categoria`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `catalogo_categoria` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `nombre` (`nombre`)
) ENGINE=InnoDB AUTO_INCREMENT=33 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `catalogo_categoria`
--

LOCK TABLES `catalogo_categoria` WRITE;
/*!40000 ALTER TABLE `catalogo_categoria` DISABLE KEYS */;
INSERT INTO `catalogo_categoria` VALUES (24,'Bolsas Herméticas'),(26,'Bolsas Negras- Blancas'),(28,'Bwol'),(31,'Cartucho transparente'),(27,'Cubiertos'),(32,'Media caja'),(25,'Papeles Aluminio'),(29,'platos'),(30,'vasos');
/*!40000 ALTER TABLE `catalogo_categoria` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `catalogo_clienteb2b`
--

DROP TABLE IF EXISTS `catalogo_clienteb2b`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `catalogo_clienteb2b` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `nombre_empresa` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `ruc` varchar(40) COLLATE utf8mb4_unicode_ci NOT NULL,
  `email_contacto` varchar(254) COLLATE utf8mb4_unicode_ci NOT NULL,
  `telefono` varchar(60) COLLATE utf8mb4_unicode_ci NOT NULL,
  `direccion` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `fecha_registro` datetime(6) NOT NULL,
  `activo` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ruc` (`ruc`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `catalogo_clienteb2b`
--

LOCK TABLES `catalogo_clienteb2b` WRITE;
/*!40000 ALTER TABLE `catalogo_clienteb2b` DISABLE KEYS */;
INSERT INTO `catalogo_clienteb2b` VALUES (10,'SUPERMERCADO EL PROGRESO S.A.','1-2345678-90-123','compras@elprogreso.example','+507 200-1234','Avenida Balboa, Ciudad de Panamá','2026-10-17 13:51:15.598826',1),(11,'DISTRIBUIDORA DEL ISTMO S.A.','1-9876543-21-000','pagos@istmo.example','+507 300-5566','Vía España, Panamá Viejo','2026-10-17 13:51:15.600289',1),(12,'TIENDAS DON PEPE','8-102-456','pedidos@donpepe.example','+507 611-2233','Calle 44, Apartado 3B, Bella Vista','2026-10-17 13:51:15.601842',1);
/*!40000 ALTER TABLE `catalogo_clienteb2b` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `catalogo_lineapedidob2b`
--

DROP TABLE IF EXISTS `catalogo_lineapedidob2b`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `catalogo_lineapedidob2b` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `subtotal` decimal(14,2) NOT NULL,
  `orden` int unsigned NOT NULL,
  `pedido_id` bigint NOT NULL,
  `producto_id` bigint NOT NULL,
  `cantidad` decimal(14,2) NOT NULL,
  `tipo_empaque` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `linea_pedido_orden_unico` (`pedido_id`,`orden`),
  KEY `catalogo_lineapedido_producto_id_977ee501_fk_catalogo_` (`producto_id`),
  CONSTRAINT `catalogo_lineapedido_pedido_id_6a96095f_fk_catalogo_` FOREIGN KEY (`pedido_id`) REFERENCES `catalogo_pedidob2b` (`id`),
  CONSTRAINT `catalogo_lineapedido_producto_id_977ee501_fk_catalogo_` FOREIGN KEY (`producto_id`) REFERENCES `catalogo_producto` (`id`),
  CONSTRAINT `catalogo_lineapedidob2b_chk_1` CHECK ((`orden` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `catalogo_lineapedidob2b`
--

LOCK TABLES `catalogo_lineapedidob2b` WRITE;
/*!40000 ALTER TABLE `catalogo_lineapedidob2b` DISABLE KEYS */;
/*!40000 ALTER TABLE `catalogo_lineapedidob2b` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `catalogo_pedidob2b`
--

DROP TABLE IF EXISTS `catalogo_pedidob2b`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `catalogo_pedidob2b` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `fecha_creacion` datetime(6) NOT NULL,
  `fecha_actualizacion` datetime(6) NOT NULL,
  `estado` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `total_estimado` decimal(14,2) NOT NULL,
  `notas` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `cliente_id` bigint NOT NULL,
  `factura_generada_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `catalogo_pedidob2b_cliente_id_031ded75_fk_catalogo_clienteb2b_id` (`cliente_id`),
  KEY `catalogo_pedidob2b_factura_generada_id_29d17aff_fk_facturaci` (`factura_generada_id`),
  CONSTRAINT `catalogo_pedidob2b_cliente_id_031ded75_fk_catalogo_clienteb2b_id` FOREIGN KEY (`cliente_id`) REFERENCES `catalogo_clienteb2b` (`id`),
  CONSTRAINT `catalogo_pedidob2b_factura_generada_id_29d17aff_fk_facturaci` FOREIGN KEY (`factura_generada_id`) REFERENCES `facturacion_factura` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `catalogo_pedidob2b`
--

LOCK TABLES `catalogo_pedidob2b` WRITE;
/*!40000 ALTER TABLE `catalogo_pedidob2b` DISABLE KEYS */;
/*!40000 ALTER TABLE `catalogo_pedidob2b` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `catalogo_producto`
--

DROP TABLE IF EXISTS `catalogo_producto`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `catalogo_producto` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `nombre` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `sku` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `descripcion_corta` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `imagen` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `precio_caja` decimal(14,2) NOT NULL,
  `precio_unidad` decimal(14,2) NOT NULL,
  `unidades_por_caja` int unsigned NOT NULL,
  `aplica_itbms` tinyint(1) NOT NULL,
  `estado_activo` tinyint(1) NOT NULL,
  `fecha_creacion` datetime(6) NOT NULL,
  `fecha_actualizacion` datetime(6) NOT NULL,
  `categoria_id` bigint NOT NULL,
  `precio_media_caja` decimal(14,2) DEFAULT NULL,
  `permite_media_caja` tinyint(1) NOT NULL,
  `codigo_barras` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `precio_consumidor` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `sku` (`sku`),
  KEY `catalogo_producto_categoria_id_19eecf17_fk_catalogo_categoria_id` (`categoria_id`),
  CONSTRAINT `catalogo_producto_categoria_id_19eecf17_fk_catalogo_categoria_id` FOREIGN KEY (`categoria_id`) REFERENCES `catalogo_categoria` (`id`),
  CONSTRAINT `catalogo_producto_chk_1` CHECK ((`unidades_por_caja` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=228 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `catalogo_producto`
--

LOCK TABLES `catalogo_producto` WRITE;
/*!40000 ALTER TABLE `catalogo_producto` DISABLE KEYS */;
INSERT INTO `catalogo_producto` VALUES (124,'Bolsa Hermética SLIDER MEDIANA (20U)','BX-S20',NULL,'productos/Bolsa_Hermética_SLIDER_MEDIANA_20U_YEYhl9N.jpg',43.54,1.81,24,1,1,'2026-10-19 00:32:42.489816','2026-10-19 01:10:23.297022',24,NULL,0,'7 595288 000024',2.59),(141,'Bolsa Hermética SLIDER GRANDE (15U)','BX-S15',NULL,'productos/Bolsa_Hermética_SLIDER_GRANDE_15U_XsnmJmd.jpg',43.54,1.81,24,1,1,'2026-10-19 00:43:05.498776','2026-10-19 00:43:05.498829',24,NULL,0,'7 595288 000017',2.59),(142,'Bolsa Hermética SLIDER GRANDE (30U)','BX-S30',NULL,'productos/Bolsa_Hermética_SLIDER_GRANDE_30U_hE2lJ4T.jpg',80.41,3.35,24,1,1,'2026-10-19 01:12:22.927780','2026-10-19 01:12:22.927829',24,NULL,0,'7 595288 000499',4.59),(143,'Bolsa Hermética SLIDER GRANDE (40U)','BX-S40',NULL,'productos/Bolsa_Hermética_SLIDER_GRANDE_40U_heAHwr7.jpg',80.41,3.35,24,1,1,'2026-10-19 01:13:43.896188','2026-10-19 01:13:43.896220',24,NULL,0,'7 595288 000505',4.59),(144,'Bolsa Hermética DOBLE CIERRE MEDIANA (24U)','BX-D24',NULL,'productos/Bolsa_Hermética_DOBLE_CIERRE_MEDIANA_24U_uWgZx8W.jpg',43.54,1.81,24,1,1,'2026-10-19 01:15:47.927310','2026-10-19 01:15:47.927342',24,NULL,0,'7 595288 000079',2.59),(145,'Bolsa Hermética DOBLE CIERRE GRANDE (19U)','BX-D19',NULL,'productos/Bolsa_Hermética_DOBLE_CIERRE_GRANDE_19U_J8vgW9Z.jpg',43.54,1.81,24,1,1,'2026-10-19 01:17:29.679848','2026-10-19 01:27:59.942153',24,NULL,0,'7 595288 000086',2.59),(146,'Bolsa Hermética DOBLE CIERRE JUMBO (10U)','BX-D10',NULL,'productos/Bolsa_Hermética_DOBLE_CIERRE_JUMBO_10U_JVWAQHX.jpg',55.19,2.30,24,1,1,'2026-10-19 01:19:21.825952','2026-10-19 01:19:21.825987',24,NULL,0,'7 595288 002448',3.29),(147,'Bolsa Hermética DOBLE CIERRE GRANDE (38U)','BX-D38',NULL,'productos/Bolsa_Hermética_DOBLE_CIERRE_GRANDE_38U_LOf1fJq.jpg',80.41,3.35,24,1,1,'2026-10-19 01:21:21.847916','2026-10-19 01:21:21.847941',24,NULL,0,'7 595288 000512',4.59),(148,'Bolsa Hermética DOBLE CIERRE MEDIANA (48U)','BX-D48',NULL,'productos/Bolsa_Hermética_DOBLE_CIERRE_MEDIANA_48U_KFfrlRZ.jpg',80.41,3.35,24,1,1,'2026-10-19 01:23:13.542942','2026-10-19 01:23:13.542972',24,NULL,0,'7 595288 000369',4.59),(149,'Bolsa Hermética CIERRE ANCHO GRANDE (20U)','BX-A20',NULL,'productos/Bolsa_Hermética_CIERRE_ANCHO_GRANDE_20U_pDLjTXq.jpg',43.54,1.81,24,1,1,'2026-10-19 01:26:05.302878','2026-10-19 01:26:05.302913',24,NULL,0,'7 595288 000437',2.59),(150,'Bolsa Hermética CIERRE ANCHO MEDIANA (25U)','BX-A25',NULL,'productos/Bolsa_Hermética_CIERRE_ANCHO_MEDIANA_25U_HINkwZw.jpg',43.54,1.81,24,1,1,'2026-10-19 01:30:14.688775','2026-10-19 01:30:14.688807',24,NULL,0,'7 595288 000444',2.59),(151,'Bolsa Hermética SANDWICH (50U)','BX-W50',NULL,'productos/Bolsa_Hermética_SANDWICH_50U_jS8h3if.jpg',36.78,1.53,24,1,1,'2026-10-19 01:31:34.765846','2026-10-19 01:31:34.765879',24,NULL,0,'7 595288 000062',2.19),(152,'Bolsa Hermética SANDWICH (100U)','BX-W100',NULL,'productos/bolsa_Hermética_SANDWICH_100U_ATRqvT1.jpg',63.71,2.61,24,1,1,'2026-10-19 01:33:29.716424','2026-10-19 01:33:29.716454',24,NULL,0,'7 595288 000321',3.79),(153,'Bolsa Hermética SNACK (40U)','BX-K40',NULL,'productos/Bolsa_Hermética_SNACK_40U_7Jk1BW8.jpg',36.15,1.51,24,1,1,'2026-10-19 01:35:13.570954','2026-10-19 01:35:13.570988',24,NULL,0,'7 595288 003087',2.15),(154,'Papel Aluminio 25 SQFT','BX-PA25',NULL,'productos/PAPEL_ALUMINIO_25_SQFT_1n8JqsG.jpg',30.00,1.25,24,1,1,'2026-10-19 01:37:20.886329','2026-10-19 01:37:20.886363',25,NULL,0,'7 595288 000390',1.75),(155,'Papel Aluminio 50 SQFT','BX-AL50',NULL,'productos/PAPEL_ALUMINIO_50_SQFT_nSOZJ48.jpg',53.52,2.23,24,1,1,'2026-10-19 01:40:40.495352','2026-10-19 01:40:40.495387',25,NULL,0,'7 595288 000406',3.19),(156,'Papel Aluminio 75 SQFT','BX-AL75',NULL,'productos/PAPEL_ALUMINIO_75_SQFT_djEuVSb.jpg',77.16,3.22,24,1,1,'2026-10-19 01:43:00.147313','2026-10-19 01:43:00.147347',25,NULL,0,'7 595288 000413',4.59),(157,'Papel Aluminio EXTRA-FUERTE 16FT','BX-PA16EF',NULL,'productos/ALUMINIO_EXTRA_FUERTE_16FT_bvltAzd.jpg',35.78,1.49,24,1,1,'2026-10-19 01:44:42.207456','2026-10-19 01:44:42.207508',25,NULL,0,'7 595288 000031',1.99),(158,'Papel Aluminio 16FT','BX-PA16',NULL,'productos/PAPEL_ALUMINIO_16FT_vFPojaA.jpg',28.04,0.93,24,1,1,'2026-10-19 01:46:11.229051','2026-10-19 01:46:11.229087',25,NULL,0,'7 595288 000048',1.25),(159,'Bolsa Negra 18x18 FLAT PEQUEÑA','BX-BNFP',NULL,'productos/BLIXI_BOLSA_NEGRA_FLAT_PEQUEÑA_1t7JgkN.jpg',65.60,0.91,80,1,1,'2026-10-20 12:57:31.659316','2026-10-20 12:57:31.659355',26,NULL,0,'7 595288 000550',1.09),(160,'Bolsa Blanca 18x18 FLAT PEQUEÑA','BX-BBFP',NULL,'productos/BLIXI_BOLSA_BLANCA_FLAT_PEQUEÑA_Ndb9jKM.jpg',65.60,0.91,80,1,1,'2026-10-20 12:59:31.326061','2026-10-20 12:59:31.326094',26,NULL,0,'7 595288 000574',1.09),(161,'Bolsa Negra 22x24 FLAT MEDIANA','BX-BNFM',NULL,'productos/BLIXI_BOLSA_NEGRA_FLAT_MEDIANA_unkKnyn.jpg',62.40,1.16,60,1,1,'2026-10-20 13:02:33.959784','2026-10-20 13:02:33.959816',26,NULL,0,'7 595288 000543',1.39),(162,'Bolsa Negra 23.5\"×30\" FLAT GRANDE','BX-BNFG',NULL,'productos/BOLSA_NEGRA_FLAT_GRANDE_9Sgtr5a.jpg',62.00,1.30,50,1,1,'2026-10-20 13:04:45.166790','2026-10-20 13:04:45.166834',26,NULL,0,'7 595288 000536',1.65),(163,'Bolsa Negra 32\"×40\" FLAT GIGANTE','BX-BNFXG',NULL,'productos/BOLSA_NEGRA_FLAT_GIGANTE_dBqkJdY.jpg',56.80,1.58,40,1,1,'2026-10-20 13:06:12.150289','2026-10-20 13:06:12.150320',26,NULL,0,'7 595288 002615',1.89),(164,'Bolsa Negra FLAT JUMBO','BX-BNFXL',NULL,'productos/BOLSA_NEGRA_FLAT_JUMBO_IWDGaMd.jpg',57.30,2.12,40,1,1,'2026-10-20 13:07:59.819375','2026-10-20 13:09:24.430621',26,NULL,0,'7 595288 000567',2.55),(165,'Bolsa Negra Agarradera Pequeña','BX-BNAP',NULL,'productos/BOLSA_NEGRA_AGARRADERA_PEQUEÑA_M9Gro0T.jpg',65.60,0.91,80,1,1,'2026-10-20 13:13:43.464268','2026-10-20 13:13:43.464306',26,NULL,0,'7 595288 002585',1.09),(166,'Bolsa Blanca Agarradera Pequeña','BX-BBAP',NULL,'productos/BOLSA_AGARRADERA_BLANCA_0rroeix.jpg',65.60,1.58,80,1,1,'2026-10-20 13:14:44.511582','2026-10-20 13:14:44.511618',26,NULL,0,'7 595288 000116',1.89),(167,'Bolsa Negra Agarradera Mediana','BX-BNAM',NULL,'productos/BOLSA_NEGRA_AGARRADERA_MEDIANA_PqBqlU9.jpg',62.40,1.16,60,1,1,'2026-10-20 13:16:51.931235','2026-10-20 13:16:51.931268',26,NULL,0,'7 7595288 8002595',1.39),(168,'Bolsa Negra Agarradera Grande','BX-BNAG',NULL,'productos/BLIXI_BOLSA_NEGRA_AGARRADERO_GRANDE_dQwItcV.jpg',71.00,1.58,50,1,1,'2026-10-20 13:18:11.314754','2026-10-20 13:32:17.307645',26,NULL,0,'7 595288 002608',1.89),(169,'Bolsa Negra Agarradera Gigante','BX-BNAXG',NULL,'productos/BLIXI_BOLSA_NEGRA_AGARRADERO_GIGANTE_JF4LiOx.jpg',78.00,2.16,40,1,1,'2026-10-20 13:19:23.010807','2026-10-20 13:19:23.010841',26,NULL,0,'7 595288 002622',2.59),(170,'Tenedor Transparente','BX-CT01',NULL,'productos/CAJA_TENEDOR_TRANSPARENTE_0YNsKfD.jpg',41.69,0.87,48,1,1,'2026-10-20 13:21:46.868564','2026-10-20 13:21:46.868598',27,NULL,0,'7 595288 002639',1.19),(171,'Cuchara Transparente','BX-CT03',NULL,'productos/CAJA_CUCHARA_TRANSPARENTE_hApjTEf.jpg',41.69,0.87,48,1,1,'2026-10-20 13:23:08.991547','2026-10-20 13:23:08.991648',27,NULL,0,'7 595288 002653',1.19),(172,'Tenedor Blanco','Bx-CB01',NULL,'productos/CAJA_TENEDOR_BLANCO_oVAJWLT.jpg',41.69,0.87,48,1,1,'2026-10-20 13:24:28.813855','2026-10-20 13:24:28.813908',27,NULL,0,'7 595288 002660',1.19),(173,'Cuchillo Transparente','BX-CT02',NULL,'productos/CAJA_CUCHILLO_TRANSPARENTE_3ueO95v.jpg',41.69,0.87,48,1,1,'2026-10-20 13:25:40.166690','2026-10-20 13:25:40.166747',27,NULL,0,'7 595288 002646',1.19),(174,'Cuchillo Blanco','BX-CB02',NULL,'productos/CAJA_CUCHILLO_BLANCO_G6moufy.jpg',41.69,0.87,48,1,1,'2026-10-20 13:26:51.064577','2026-10-20 13:26:51.064609',27,NULL,0,'7 595288 002677',1.19),(175,'Cuchara Blanco','Bx-CB03',NULL,'productos/BLIXI_CUCHARA_BLANCO_bq5hGGm.jpg',41.69,0.87,48,1,1,'2026-10-20 13:28:24.839075','2026-10-20 13:28:24.839120',27,NULL,0,'7 595288 002684',1.19),(176,'Bwol Blanco 7 (20U)','BX-PL07',NULL,'productos/BWOL_BLANCO_7_x4vF07j.jpg',31.28,1.30,24,1,1,'2026-10-20 13:34:38.127635','2026-10-20 13:38:23.195020',28,NULL,0,'7 595288 002738',1.79),(177,'Plato Blanco 8 (25U)','BX-PL8',NULL,'productos/PLATO_BLANCO_8_bj4APW8.jpg',39.42,1.64,24,1,1,'2026-10-20 13:36:07.743850','2026-10-20 13:37:56.400987',29,NULL,0,'7 595288 002707',2.25),(178,'Plato Blanco 9 (25U)','BX-PL9',NULL,'productos/PLATO_BLANCO_9__PdYIXoZ.jpg',43.62,1.82,24,1,1,'2026-10-20 13:37:31.538342','2026-10-20 13:37:31.538375',29,NULL,0,'7 595288 002714',2.49),(179,'Bwol Blanco 10 (20U)','BX-PL10',NULL,'productos/BWOL_BLANCO_10__ME8pQOH.jpg',49.93,2.08,24,1,1,'2026-10-20 13:39:48.081216','2026-10-20 13:39:48.081249',28,NULL,0,'7 595288 002721',2.85),(180,'Vasos Blancos 16 ONZ (25U)','BX-VB16',NULL,'productos/VASOS_BLANCOS_16_25U_3NJ7Gep.jpg',83.75,1.74,48,1,1,'2026-10-20 13:44:37.434821','2026-10-20 13:44:37.434857',30,NULL,0,'7 451111 582313',2.39),(181,'Vasos Blancos 10 ONZ (25U)','BX-BV10',NULL,'productos/VASOS_BLANCOS_10_25U_DTLc74R.jpg',54.31,1.13,48,1,1,'2026-10-20 13:46:00.336498','2026-10-20 13:46:00.336535',30,NULL,0,'7 595288 002806',1.55),(182,'Vasos Blancos 12 ONZ (25U)','BX-BV12',NULL,'productos/VASOS_BLANCOS_12_ONZA_25_UNIDADES_21KPSop.jpg',64.82,1.35,48,1,1,'2026-10-20 13:47:12.920109','2026-10-20 13:47:12.920143',30,NULL,0,'7 595288 002813',1.85),(183,'Vasos Transparentes 16 ONZ (25U)','BX-VT16',NULL,'productos/VASOS_TRANSPARENTES_16_ONZAS_25_UNIDADES_xe3bX5x.jpg',83.75,1.74,48,1,1,'2026-10-20 13:48:54.380820','2026-10-20 13:48:54.380867',30,NULL,0,'7 451111 582290',2.39),(184,'Vasos Transparentes 10 ONZ (25U)','BX-VT10',NULL,'productos/VASOS_TRANSPARENTES_10_ONZAS_25_UND_Y6ooeln.jpg',54.31,1.13,48,1,1,'2026-10-20 13:50:10.731781','2026-10-20 13:50:10.731819',30,NULL,0,'7 595288 002837',1.55),(185,'Vasos Transparentes 12 ONZ (25U)','BX-VT12',NULL,'productos/VASOS_TRANSPARENTES_12_ONZ_25_UND_lE0eUTN.jpg',64.82,1.35,48,1,1,'2026-10-20 13:51:23.973572','2026-10-20 13:51:23.973608',30,NULL,0,'7 595288 002844',1.85),(186,'Vasos Transparentes Duros 10 ONZ (25U)','BX-VD10',NULL,'productos/VASOS_TRANSPARENTES_DUROS_10_ONZ_25_UND_RbTJJzn.jpg',75.34,1.57,48,1,1,'2026-10-20 13:52:41.304064','2026-10-20 13:52:41.304098',30,NULL,0,'7 595288 003063',2.15),(187,'Vasos Transparentes Duros 12 ONZ (25U)','BX-VD12',NULL,'productos/VASOS_TRANSPARENTES_DUROS_12_ONZ_25_UND_jhF2k4F.jpg',85.49,1.79,48,1,1,'2026-10-20 13:54:03.751905','2026-10-20 13:54:03.751966',30,NULL,0,'7 595288 003070',2.45),(188,'Cartucho Transparente 3×9 (100U)','BX-F39',NULL,'productos/CARTUCHO_TRANSPARENTE_39_100U_Q4DiCGo.jpg',103.67,0.35,300,1,1,'2026-10-20 14:07:33.803819','2026-10-20 14:07:33.803861',31,NULL,0,'7 595288 003094',0.49),(189,'Cartucho Transparente 5×10 (100U)','BX-F510',NULL,'productos/CARTUCHO_TRANSPARENTE_510_100U_a4dES3V.jpg',118.83,0.59,200,1,1,'2026-10-20 14:08:55.533101','2026-10-20 14:08:55.533144',31,NULL,0,'7 595288 003100',0.85),(190,'Cartucho Transparente 6×12 (100U)','BX-F612',NULL,'productos/CARTUCHO_TRANSPARENTE_612_100U_49HzTn8.jpg',114.69,0.76,150,1,1,'2026-10-20 14:11:48.305470','2026-10-20 14:11:48.305504',31,NULL,0,'7 595288 003117',1.09),(191,'Cartucho Transparente 7×12 (100U)','BX-F712',NULL,'productos/CARTUCHO_TRANSPARENTE_712_100U_fqM8uDx.jpg',124.95,0.83,150,1,1,'2026-10-20 14:13:09.285065','2026-10-20 14:13:09.285105',31,NULL,0,'7 595288 003124',1.19),(192,'Cartucho Transparente 8×14 (100U)','BX- F510',NULL,'',104.21,1.04,100,1,1,'2026-10-20 14:15:27.175842','2026-10-20 14:15:27.175872',31,NULL,0,'7 595288 003131',1.49),(193,'Cartucho Transparente 10×15 (100U)','BX-F1015',NULL,'productos/CARTUCHO_TRANSPARENTE_1015_100U_d57R5py.jpg',120.50,1.51,80,1,1,'2026-10-20 14:16:28.959696','2026-10-20 14:16:28.959728',31,NULL,0,'7 595288 003148',2.15),(194,'Media Caja Bolsa Negra FLAT PEQUEÑA','PK-BNFP',NULL,'productos/MEDIA_CAJA_BOLSA_NEGRA_FLAT_PEQUEÑA.jpg',65.60,0.82,40,1,1,'2026-10-20 14:20:17.883386','2026-10-20 14:20:47.533334',32,32.80,1,NULL,1.09),(195,'Media Caja Bolsa Blanca FLAT PEQUEÑA','PK-BBFP',NULL,'productos/MEDIAS_CAJA_BOLSA_BLANCA_FLAT_PEQUEÑA.jpg',32.80,0.82,40,1,1,'2026-10-20 23:14:25.786224','2026-10-20 23:16:03.167865',32,32.80,1,NULL,1.09),(196,'Media Caja Bolsa Negra FLAT MEDIANA','PK-BNFM',NULL,'productos/MEDIAS_CAJA_BOLSA_NEGRA_FLAT_MEDIANA.jpg',31.20,1.04,30,1,1,'2026-10-20 23:37:31.440344','2026-10-20 23:37:31.440372',32,31.20,1,NULL,1.39),(197,'Media Caja Bolsa Negra FLAT GRANDE','PK-BNFG',NULL,'productos/MEDIAS_CAJA_BOLSA_NEGRA_FLAT_GRANDE_23.5__30.jpg',31.00,1.24,25,1,1,'2026-10-20 23:38:59.342685','2026-10-20 23:38:59.342722',32,31.00,1,NULL,1.65),(198,'Media Caja Bolsa Negra FLAT GIGANTE','PK-BNFXG',NULL,'productos/MEDIA_CAJA_BOLSA_NEGRA_FLAT_GIGANTE.jpg',28.40,1.42,20,1,1,'2026-10-20 23:42:36.936393','2026-10-20 23:42:36.936428',32,28.40,1,NULL,1.89),(199,'Media Caja Bolsa Negra FLAT JUMBO','PK-BNFXL',NULL,'productos/MEDIA_CAJABOLSA_NEGRA_FLAT_JUMBO_37.5__50.jpg',28.65,1.91,15,1,1,'2026-10-20 23:43:33.529207','2026-10-20 23:43:33.529243',32,28.65,1,NULL,2.55),(200,'Media Caja Bolsa Agarradera Pequeña','PK-BNAP',NULL,'productos/BOLSA_NEGRA_AGARRADERA_PEQUEÑA_NonrmwX.jpg',32.80,0.82,40,1,1,'2026-10-20 23:44:52.799020','2026-10-20 23:44:52.799047',32,32.80,1,NULL,1.09),(201,'Media Caja Bolsa Blanca Agarradera Pequeña','PK-BBAP',NULL,'productos/BOLSA_AGARRADERA_BLANCA_4bbUH4P.jpg',32.80,0.82,40,1,1,'2026-10-20 23:46:13.077641','2026-10-20 23:46:13.077669',32,32.80,1,NULL,1.09),(202,'Media Caja Bolsa Negra Agarradera Mediana','PK-BNAM',NULL,'productos/BOLSA_NEGRA_AGARRADERA_MEDIANA_BPEITnG.jpg',31.20,1.04,30,1,1,'2026-10-20 23:47:16.233425','2026-10-20 23:47:16.233454',32,31.20,1,NULL,1.39),(203,'Media Caja Bolsa Negra Agarradera Grande','PK-BNAG',NULL,'productos/BLIXI_BOLSA_NEGRA_AGARRADERO_GRANDE_BTbiyMR.jpg',35.50,1.42,25,1,1,'2026-10-20 23:48:16.225714','2026-10-21 00:11:11.664900',32,35.50,1,NULL,1.89),(204,'Media Caja Bolsa Negra Agarradera Gigante','PK-BNAXG',NULL,'productos/BLIXI_BOLSA_NEGRA_AGARRADERO_GIGANTE_OqiXcCs.jpg',39.00,1.95,20,1,1,'2026-10-20 23:49:23.496605','2026-10-20 23:49:23.496640',32,39.00,1,NULL,2.59),(205,'Media Caja SLIDER MEDIANA (20U)','PK-S20',NULL,'productos/Bolsa_Hermética_SLIDER_MEDIANA_20U_fzcqa3n.jpg',21.77,1.81,12,1,1,'2026-10-20 23:51:44.951069','2026-10-20 23:51:44.951103',32,21.77,1,NULL,2.59),(206,'Media Caja SLIDER GRANDE (12U)','PK-S15',NULL,'productos/Bolsa_Hermética_SLIDER_GRANDE_15U_yeMISHH.jpg',21.77,1.81,12,1,1,'2026-10-20 23:52:51.990390','2026-10-20 23:52:51.990434',32,21.77,1,NULL,2.59),(207,'Media Caja SLIDER Doble Cierre Grande (19U)','PK-DC19',NULL,'productos/Bolsa_Hermética_DOBLE_CIERRE_GRANDE_19U_GcRrRAR.jpg',21.77,1.81,12,1,1,'2026-10-20 23:54:33.585392','2026-10-20 23:54:33.585423',32,21.77,1,NULL,2.59),(208,'Media Caja SLIDER Doble Cierre Mediano (24U)','PK-DC24',NULL,'productos/Bolsa_Hermética_DOBLE_CIERRE_MEDIANA_24U_xZkOR1y.jpg',21.77,1.81,12,1,1,'2026-10-20 23:56:08.522537','2026-10-20 23:56:08.522578',32,21.77,1,NULL,2.59),(209,'Media Caja SLIDER Cierre Ancho Mediano (25U)','PK-CA25',NULL,'productos/Bolsa_Hermética_CIERRE_ANCHO_MEDIANA_25U_FhHiXMG.jpg',21.77,1.81,12,1,1,'2026-10-20 23:57:42.733183','2026-10-20 23:57:42.733208',32,21.77,1,NULL,2.59),(210,'Media Caja SLIDER Cierre Ancho Grande (20U)','PK-CA20',NULL,'productos/Bolsa_Hermética_CIERRE_ANCHO_GRANDE_20U_Sn3Xj9D.jpg',21.77,1.81,12,1,1,'2026-10-21 00:01:59.261611','2026-10-21 00:01:59.261641',32,21.77,1,NULL,2.59),(211,'Media Caja SLIDER SANDWICH (50U)','PK-W50',NULL,'productos/Bolsa_Hermética_SANDWICH_50U_IsLaHKM.jpg',18.39,1.53,12,1,1,'2026-10-21 00:03:24.287116','2026-10-21 00:03:24.287179',32,18.39,1,NULL,2.19),(212,'Media Caja Cuchara Transparente (25U)','PK-CT03',NULL,'productos/CAJA_CUCHARA_TRANSPARENTE_49e0haa.jpg',20.01,0.83,24,1,1,'2026-10-21 00:08:52.906546','2026-10-21 00:08:52.906579',32,20.01,1,NULL,1.19),(213,'Media Caja Cuchara Blanca (25U)','PK-CB03',NULL,'productos/BLIXI_CUCHARA_BLANCO_Ly0bpu6.jpg',20.01,0.83,24,1,1,'2026-10-21 00:09:40.737328','2026-10-21 00:09:40.737359',32,20.01,1,NULL,1.19),(214,'Media Caja Tenedor Transparente (25U)','PK-CT01',NULL,'productos/CAJA_TENEDOR_TRANSPARENTE_yQBCKWN.jpg',20.01,0.83,24,1,1,'2026-10-21 00:10:43.411951','2026-10-21 00:10:43.412003',32,20.01,1,NULL,1.19),(215,'Media Caja Tenedor Blanco (25U)','PK-CB01',NULL,'productos/CAJA_TENEDOR_BLANCO_j4V9uE0.jpg',20.01,0.83,24,1,1,'2026-10-21 00:12:27.876081','2026-10-21 00:12:27.876109',32,20.01,1,NULL,1.19),(216,'Media Caja Vasos Blancos 16 ONZ (25U)','PK-VB16',NULL,'productos/VASOS_BLANCOS_16_25U_whcosoK.jpg',41.88,1.74,24,1,1,'2026-10-21 00:16:41.006400','2026-10-21 00:16:41.006437',32,41.88,1,NULL,2.39),(217,'Media Caja Vasos Blancos 10 ONZ (25U)','PK-VB10',NULL,'productos/VASOS_BLANCOS_10_25U_RJLcTfZ.jpg',27.15,1.13,24,1,1,'2026-10-21 00:17:44.254691','2026-10-21 00:17:44.254727',32,27.15,1,NULL,1.55),(218,'Media Caja Vasos Blancos 12 ONZ (25U)','PK-VB12',NULL,'productos/VASOS_BLANCOS_12_ONZA_25_UNIDADES_PvyTv2q.jpg',32.41,1.35,24,1,1,'2026-10-21 00:18:55.617811','2026-10-21 00:18:55.617854',32,32.41,1,NULL,1.85),(219,'Media Caja Vasos Transparentes 16 ONZ (25U)','PK-VT16',NULL,'productos/VASOS_TRANSPARENTES_16_ONZAS_25_UNIDADES_Cl4i0bl.jpg',41.88,1.74,24,1,1,'2026-10-21 00:21:40.281524','2026-10-21 00:21:40.281548',32,41.88,1,NULL,2.39),(220,'Media Caja Vasos Transparentes 10 ONZ (25U)','PK-VT10',NULL,'productos/VASOS_TRANSPARENTES_10_ONZAS_25_UND_9iSN7em.jpg',27.15,1.13,24,1,1,'2026-10-21 00:22:53.654778','2026-10-21 00:22:53.654804',32,27.15,1,NULL,1.55),(221,'Media Caja Vasos Transparentes 12 ONZ (25U)','PK-VT12',NULL,'productos/VASOS_TRANSPARENTES_12_ONZ_25_UND_NnF0jrF.jpg',32.41,1.35,24,1,1,'2026-10-21 00:24:16.310433','2026-10-21 00:24:16.310475',32,32.41,1,NULL,1.85),(222,'Media Caja Vasos Transparentes Duros 10 ONZ (25U)','PK-VD10',NULL,'productos/VASOS_TRANSPARENTES_DUROS_10_ONZ_25_UND_kjhLN1m.jpg',32.41,1.35,24,1,1,'2026-10-21 00:25:32.055093','2026-10-21 00:25:32.055119',32,32.41,1,NULL,1.85),(223,'Media Caja Vasos Transparentes Duros 12 ONZ (25U)','PK-VD12',NULL,'productos/VASOS_TRANSPARENTES_DUROS_12_ONZ_25_UND_Kwp1bzy.jpg',42.75,1.79,24,1,1,'2026-10-21 00:26:51.836630','2026-10-21 00:26:51.836664',32,42.75,1,NULL,2.45),(224,'Media Caja Papel Aluminio 16 FT','BX-PAL75',NULL,'productos/PAPEL_ALUMINIO_16FT_Q67lxFk.jpg',11.22,0.93,15,1,1,'2026-10-21 00:29:05.039176','2026-10-21 00:31:00.166891',32,11.22,1,'7 595288 000413',1.25),(225,'Media Caja Papel Aluminio 25 FT','BLX-PA25',NULL,'productos/PAPEL_ALUMINIO_25_SQFT_ToSgqeV.jpg',15.00,1.25,12,1,1,'2026-10-21 00:32:46.019324','2026-10-21 00:32:46.019343',32,15.00,1,'7 595288 000390',1.75),(226,'Media Caja Papel Aluminio 50 FT','BLX-PA50',NULL,'productos/PAPEL_ALUMINIO_50_SQFT_Y6eNGjt.jpg',26.76,2.23,12,1,1,'2026-10-21 00:35:47.322527','2026-10-21 00:35:47.322546',32,26.76,1,'7 595288 000406',3.19),(227,'Media Caja Papel Aluminio EXTRA-FUERTE 16 FT','BLX-PA16EF',NULL,'productos/ALUMINIO_EXTRA_FUERTE_16FT_KA0RPUV.jpg',17.89,1.49,12,1,1,'2026-10-21 00:37:42.047941','2026-10-21 00:37:42.047960',32,17.89,1,'7 595288 000031',1.99);
/*!40000 ALTER TABLE `catalogo_producto` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_admin_log`
--

DROP TABLE IF EXISTS `django_admin_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_admin_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext COLLATE utf8mb4_unicode_ci,
  `object_repr` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `action_flag` smallint unsigned NOT NULL,
  `change_message` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `content_type_id` int DEFAULT NULL,
  `user_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_auth_user_id` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `django_admin_log_chk_1` CHECK ((`action_flag` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=232 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_admin_log`
--

LOCK TABLES `django_admin_log` WRITE;
/*!40000 ALTER TABLE `django_admin_log` DISABLE KEYS */;
INSERT INTO `django_admin_log` VALUES (1,'2026-10-04 17:38:03.086063','19','rwgrwgargeg - Bolsa de Basura Blixi',1,'[{\"added\": {}}]',15,2),(2,'2026-10-04 17:38:46.983282','19','rwgrwgargeg - Bolsa de Basura Blixi',2,'[{\"changed\": {\"fields\": [\"Imagen\"]}}]',15,2),(3,'2026-10-04 17:41:53.591648','20','gfwgfdsf - Bolsa Blixi',1,'[{\"added\": {}}]',15,2),(4,'2026-10-04 17:43:26.981171','21','gw4g4h43 - Cucharas Blixi',1,'[{\"added\": {}}]',15,2),(5,'2026-10-04 17:43:43.545888','10','CLO-001 - Cloro desinfectante 2 L',3,'',15,2),(6,'2026-10-16 12:52:40.238646','23','BH-002 - Bolsa Hermética 10x12',3,'',15,2),(7,'2026-10-16 12:52:40.238681','22','BH-001 - Bolsa Hermética 8x10',3,'',15,2),(8,'2026-10-16 12:52:40.238694','27','BN-002 - Bolsa Blanca Grande',3,'',15,2),(9,'2026-10-16 12:52:40.238704','26','BN-001 - Bolsa Negra Mediana',3,'',15,2),(10,'2026-10-16 12:52:40.238714','30','BW-001 - Servilletas BWOL',3,'',15,2),(11,'2026-10-16 12:52:40.238723','31','BW-002 - Servilletas BWOL Premium',3,'',15,2),(12,'2026-10-16 12:52:40.238732','37','CT-002 - Cartucho 1000ml',3,'',15,2),(13,'2026-10-16 12:52:40.238740','36','CT-001 - Cartucho 500ml',3,'',15,2),(14,'2026-10-16 12:52:40.238749','29','CU-002 - Cucharas de Sopa',3,'',15,2),(15,'2026-10-16 12:52:40.238758','28','CU-001 - Tenedores de Mesa',3,'',15,2),(16,'2026-10-16 12:52:40.238766','24','PA-001 - Papel Aluminio 40cm',3,'',15,2),(17,'2026-10-16 12:52:40.238775','25','PA-002 - Papel Aluminio 45cm',3,'',15,2),(18,'2026-10-16 12:52:40.238783','33','PL-002 - Platos Desechables 10',3,'',15,2),(19,'2026-10-16 12:52:40.238791','32','PL-001 - Platos Desechables 9',3,'',15,2),(20,'2026-10-16 12:52:40.238799','34','VA-001 - Vasos Plásticos 12oz',3,'',15,2),(21,'2026-10-16 12:52:40.238809','35','VA-002 - Vasos Plásticos 16oz',3,'',15,2),(22,'2026-10-16 12:52:54.108718','5','DISTRIBUIDORA DEL ISTMO S.A. (1-9876543-21-000)',3,'',13,2),(23,'2026-10-16 12:52:54.108751','4','SUPERMERCADO EL PROGRESO S.A. (1-2345678-90-123)',3,'',13,2),(24,'2026-10-16 12:52:54.108761','6','TIENDAS DON PEPE (8-102-456)',3,'',13,2),(25,'2026-10-16 12:53:11.475353','15','Cartuchos Transparentes',2,'[{\"changed\": {\"fields\": [\"Nombre\"]}}]',16,2),(26,'2026-10-16 13:07:54.058258','54','7 595288 000024 - Bolsa Hermética SLIDER MEDIANA (20U)',1,'[{\"added\": {}}]',15,2),(27,'2026-10-16 13:08:32.806540','39','BH-002 - Bolsa Hermética 10x12',3,'',15,2),(28,'2026-10-16 13:08:32.806568','38','BH-001 - Bolsa Hermética 8x10',3,'',15,2),(29,'2026-10-16 13:08:32.806579','43','BN-002 - Bolsa Blanca Grande',3,'',15,2),(30,'2026-10-16 13:08:32.806588','42','BN-001 - Bolsa Negra Mediana',3,'',15,2),(31,'2026-10-16 13:08:32.806596','46','BW-001 - Servilletas BWOL',3,'',15,2),(32,'2026-10-16 13:08:32.806603','47','BW-002 - Servilletas BWOL Premium',3,'',15,2),(33,'2026-10-16 13:08:32.806611','53','CT-002 - Cartucho 1000ml',3,'',15,2),(34,'2026-10-16 13:08:32.806619','52','CT-001 - Cartucho 500ml',3,'',15,2),(35,'2026-10-16 13:08:32.806626','45','CU-002 - Cucharas de Sopa',3,'',15,2),(36,'2026-10-16 13:08:32.806634','44','CU-001 - Tenedores de Mesa',3,'',15,2),(37,'2026-10-16 13:08:32.806642','40','PA-001 - Papel Aluminio 40cm',3,'',15,2),(38,'2026-10-16 13:08:32.806650','41','PA-002 - Papel Aluminio 45cm',3,'',15,2),(39,'2026-10-16 13:08:32.806657','49','PL-002 - Platos Desechables 10',3,'',15,2),(40,'2026-10-16 13:08:32.806664','48','PL-001 - Platos Desechables 9',3,'',15,2),(41,'2026-10-16 13:08:32.806673','50','VA-001 - Vasos Plásticos 12oz',3,'',15,2),(42,'2026-10-16 13:08:32.806681','51','VA-002 - Vasos Plásticos 16oz',3,'',15,2),(43,'2026-10-16 13:11:38.520526','55','7 595288 000017 - Bolsa Hermética SLIDER GRANDE (15U)',1,'[{\"added\": {}}]',15,2),(44,'2026-10-16 13:13:41.390226','56','7 595288 000499 - Bolsa Hermética SLIDER GRANDE (30U)',1,'[{\"added\": {}}]',15,2),(45,'2026-10-16 13:15:25.822436','57','7 595288 000505 - Bolsa Hermética SLIDER GRANDE (40U)',1,'[{\"added\": {}}]',15,2),(46,'2026-10-16 13:15:39.166751','56','7 595288 000499 - Bolsa Hermética SLIDER GRANDE (30U)',2,'[{\"changed\": {\"fields\": [\"Precio por unidad\"]}}]',15,2),(47,'2026-10-16 13:19:19.648667','58','7 595288 000079 - Bolsa Hermética DOBLE CIERRE MEDIANA (24U)',1,'[{\"added\": {}}]',15,2),(48,'2026-10-16 13:22:14.436815','59','7 595288 003087 - Bolsa Hermética SNACK (40U)',1,'[{\"added\": {}}]',15,2),(49,'2026-10-16 13:23:53.028262','60','7 595288 000321 - Bolsa Hermética SANDWICH (100U)',1,'[{\"added\": {}}]',15,2),(50,'2026-10-16 13:25:11.321902','61','7 595288 000062 - Bolsa Hermética SANDWICH (50U)',1,'[{\"added\": {}}]',15,2),(51,'2026-10-16 13:26:36.816682','62','7 595288 000444 - Bolsa Hermética CIERRE ANCHO MEDIANA (25U)',1,'[{\"added\": {}}]',15,2),(52,'2026-10-16 13:28:27.685015','63','7 595288 000437 - Bolsa Hermética CIERRE ANCHO GRANDE (20U)',1,'[{\"added\": {}}]',15,2),(53,'2026-10-16 13:29:44.023086','64','7 595288 000369 - Bolsa Hermética DOBLE CIERRE MEDIANA (48U)',1,'[{\"added\": {}}]',15,2),(54,'2026-10-16 13:31:04.052291','65','7 595288 000512 - Bolsa Hermética DOBLE CIERRE GRANDE (38U)',1,'[{\"added\": {}}]',15,2),(55,'2026-10-16 13:32:21.370947','66','7 595288 002448 - Bolsa Hermética DOBLE CIERRE JUMBO (10U)',1,'[{\"added\": {}}]',15,2),(56,'2026-10-16 13:33:38.042009','67','7 595288 000086 - Bolsa Hermética DOBLE CIERRE GRANDE (19U)',1,'[{\"added\": {}}]',15,2),(57,'2026-10-17 12:33:09.440204','68','7 595288 000390 - Papel Aluminio 25 SQFT',1,'[{\"added\": {}}]',15,2),(58,'2026-10-17 12:34:50.275392','69','7 595288 000406 - Papel Aluminio 50 SQFT',1,'[{\"added\": {}}]',15,2),(59,'2026-10-17 12:36:12.293647','70','7 595288 000413 - Papel Aluminio 75 SQFT',1,'[{\"added\": {}}]',15,2),(60,'2026-10-17 12:38:05.215554','71','7 595288 000031 - Aluminio Extra Fuerte 16FT',1,'[{\"added\": {}}]',15,2),(61,'2026-10-17 12:39:47.357849','72','7 595288 000048 - Papel Aluminio 16FT',1,'[{\"added\": {}}]',15,2),(62,'2026-10-17 12:44:03.056293','73','7 595288 000550 - Bolsa Negra 18x18 Flat Pequeña',1,'[{\"added\": {}}]',15,2),(63,'2026-10-17 12:46:13.125307','74','7 595288 000574 - Bolsa Blanca 18x18 Flat Pequeña',1,'[{\"added\": {}}]',15,2),(64,'2026-10-17 12:47:57.452226','75','7 595288 000543 - Bolsa Negra 22x24 Flat Mediana',1,'[{\"added\": {}}]',15,2),(65,'2026-10-17 12:49:14.510042','76','7 595288 000536 - Bolsa Negra 23.5\"x30\" Flat Grande',1,'[{\"added\": {}}]',15,2),(66,'2026-10-17 12:50:23.653187','77','7 595288 002615 - Bolsa Negra 32\"x40\" Flat Gigante',1,'[{\"added\": {}}]',15,2),(67,'2026-10-17 12:51:58.052062','78','7 595288 000567 - Bolsa Negra 37.5\"x50\"',1,'[{\"added\": {}}]',15,2),(68,'2026-10-17 12:55:00.009037','79','7 595288 002585 - Bolsa Negra 18x18 Agarradera Pequeña',1,'[{\"added\": {}}]',15,2),(69,'2026-10-17 12:56:36.256341','80','7 595288 000116 - Bolsa Blanca 18x18 Agarradera Pequeña',1,'[{\"added\": {}}]',15,2),(70,'2026-10-17 12:58:45.822714','81','7 75595288 8002595 - Bolsa Negra 22x24 Agarradera Mediana',1,'[{\"added\": {}}]',15,2),(71,'2026-10-17 13:00:36.365287','82','7 595288 002608 - Bolsa Negra 23.5x30 Agarradera Grande',1,'[{\"added\": {}}]',15,2),(72,'2026-10-17 13:02:25.494567','83','7 595288 002622 - Bolsa Negra 32x40 Agarradera Gigante',1,'[{\"added\": {}}]',15,2),(73,'2026-10-17 13:05:23.510055','84','7 595288 002639 - Tenedor Transparente',1,'[{\"added\": {}}]',15,2),(74,'2026-10-17 13:06:02.394696','58','7 595288 000079 - Bolsa Hermética DOBLE CIERRE MEDIANA (24U)',2,'[{\"changed\": {\"fields\": [\"Precio por media caja\", \"\\u00bfPermite venta por media caja?\"]}}]',15,2),(75,'2026-10-17 13:06:15.840881','54','7 595288 000024 - Bolsa Hermética SLIDER MEDIANA (20U)',2,'[{\"changed\": {\"fields\": [\"Precio por media caja\", \"\\u00bfPermite venta por media caja?\"]}}]',15,2),(76,'2026-10-17 13:08:20.959425','85','7 595288 002653 - Cuchara Transparente',1,'[{\"added\": {}}]',15,2),(77,'2026-10-17 13:09:46.707766','86','7 595288 002660 - Tenedor Blanco',1,'[{\"added\": {}}]',15,2),(78,'2026-10-17 13:10:52.177407','87','7 595288 002646 - Cuchillo Transparente',1,'[{\"added\": {}}]',15,2),(79,'2026-10-17 13:11:40.817946','88','7 595288 002677 - Cuchillo Blanco',1,'[{\"added\": {}}]',15,2),(80,'2026-10-17 13:12:32.890204','89','7 595288 002684 - Cuchara Blanco',1,'[{\"added\": {}}]',15,2),(81,'2026-10-17 13:14:14.737693','90','7 595288 002738 - Bwol Blanco 7',1,'[{\"added\": {}}]',15,2),(82,'2026-10-17 13:15:15.207656','91','7 595288 002707 - Plato Blanco 8',1,'[{\"added\": {}}]',15,2),(83,'2026-10-17 13:16:58.247826','92','7 595288 002714 - Plato Blanco 9',1,'[{\"added\": {}}]',15,2),(84,'2026-10-17 13:19:41.757743','93','7 595288 002721 - Bwol Blanco 10',1,'[{\"added\": {}}]',15,2),(85,'2026-10-17 13:23:01.083031','94','7 595288 582313 - Vasos Blancos 16 (25U)',1,'[{\"added\": {}}]',15,2),(86,'2026-10-17 13:24:21.822853','95','7 595288 002806 - Vasos Blancos 10 (25U)',1,'[{\"added\": {}}]',15,2),(87,'2026-10-17 13:26:19.859027','96','7 595288 002813 - Vasos Blancos 12 onza (25U)',1,'[{\"added\": {}}]',15,2),(88,'2026-10-17 13:27:57.897037','97','7 451111 582290 - Vasos Transparentes 16 onzas (25U)',1,'[{\"added\": {}}]',15,2),(89,'2026-10-17 13:28:10.966757','96','7 595288 002813 - Vasos Blancos 12 onzas (25U)',2,'[{\"changed\": {\"fields\": [\"Nombre del producto\"]}}]',15,2),(90,'2026-10-17 13:29:50.285650','98','7 595288 002837 - Vasos Transparentes 10 onzas (25U)',1,'[{\"added\": {}}]',15,2),(91,'2026-10-17 13:32:39.303531','99','7 595288 002844 - Vasos Transparentes 12 onzas (25U)',1,'[{\"added\": {}}]',15,2),(92,'2026-10-17 13:33:52.277813','100','7 595288 003063 - Vasos Transparentes Duros 10 onzas (25U)',1,'[{\"added\": {}}]',15,2),(93,'2026-10-17 13:35:12.906734','101','7 595288 003070 - Vasos Transparentes Duros 12 onzas (25U)',1,'[{\"added\": {}}]',15,2),(94,'2026-10-17 13:37:50.895256','102','7 595288 003094 - Cartucho Transparente 3x9 (100U)',1,'[{\"added\": {}}]',15,2),(95,'2026-10-17 13:39:36.758466','103','7 595288 003100 - Cartucho Transparente 5x10 (100U)',1,'[{\"added\": {}}]',15,2),(96,'2026-10-17 13:41:04.905906','104','7 595288 003117 - Cartucho Transparente 6x12 (100U)',1,'[{\"added\": {}}]',15,2),(97,'2026-10-17 13:42:05.115755','105','7 595288 003124 - Cartucho Transparente 7x12 (100U)',1,'[{\"added\": {}}]',15,2),(98,'2026-10-17 13:43:24.279139','106','7 595288 003131 - Cartucho Transparente 8x14 (100U)',1,'[{\"added\": {}}]',15,2),(99,'2026-10-17 13:44:39.347467','107','7 595288 003148 - Cartucho Transparente 10x15 (100U)',1,'[{\"added\": {}}]',15,2),(100,'2026-10-19 00:24:22.044609','109','BH-002 - Bolsa Hermética 10x12',3,'',15,2),(101,'2026-10-19 00:24:22.044662','108','BH-001 - Bolsa Hermética 8x10',3,'',15,2),(102,'2026-10-19 00:24:22.044682','113','BN-002 - Bolsa Blanca Grande',3,'',15,2),(103,'2026-10-19 00:24:22.044698','112','BN-001 - Bolsa Negra Mediana',3,'',15,2),(104,'2026-10-19 00:24:22.044713','116','BW-001 - Servilletas BWOL',3,'',15,2),(105,'2026-10-19 00:24:22.044726','117','BW-002 - Servilletas BWOL Premium',3,'',15,2),(106,'2026-10-19 00:24:22.044740','123','CT-002 - Cartucho 1000ml',3,'',15,2),(107,'2026-10-19 00:24:22.044752','122','CT-001 - Cartucho 500ml',3,'',15,2),(108,'2026-10-19 00:24:22.044764','115','CU-002 - Cucharas de Sopa',3,'',15,2),(109,'2026-10-19 00:24:22.044779','114','CU-001 - Tenedores de Mesa',3,'',15,2),(110,'2026-10-19 00:24:22.044793','110','PA-001 - Papel Aluminio 40cm',3,'',15,2),(111,'2026-10-19 00:24:22.044806','111','PA-002 - Papel Aluminio 45cm',3,'',15,2),(112,'2026-10-19 00:24:22.044819','119','PL-002 - Platos Desechables 10',3,'',15,2),(113,'2026-10-19 00:24:22.044831','118','PL-001 - Platos Desechables 9',3,'',15,2),(114,'2026-10-19 00:24:22.044843','120','VA-001 - Vasos Plásticos 12oz',3,'',15,2),(115,'2026-10-19 00:24:22.044856','121','VA-002 - Vasos Plásticos 16oz',3,'',15,2),(116,'2026-10-19 00:32:42.491253','124','sds - Bolsa Hermética SLIDER MEDIANA (20U)',1,'[{\"added\": {}}]',15,2),(117,'2026-10-19 00:33:04.074261','124','sds - Bolsa Hermética SLIDER MEDIANA (20U)',2,'[{\"changed\": {\"fields\": [\"Imagen\"]}}]',15,2),(118,'2026-10-19 00:40:11.136905','126','BH-002 - Bolsa Hermética 10x12',3,'',15,2),(119,'2026-10-19 00:40:11.136954','125','BH-001 - Bolsa Hermética 8x10',3,'',15,2),(120,'2026-10-19 00:40:11.136975','130','BN-002 - Bolsa Blanca Grande',3,'',15,2),(121,'2026-10-19 00:40:11.136991','129','BN-001 - Bolsa Negra Mediana',3,'',15,2),(122,'2026-10-19 00:40:11.137007','133','BW-001 - Servilletas BWOL',3,'',15,2),(123,'2026-10-19 00:40:11.137020','134','BW-002 - Servilletas BWOL Premium',3,'',15,2),(124,'2026-10-19 00:40:11.137033','140','CT-002 - Cartucho 1000ml',3,'',15,2),(125,'2026-10-19 00:40:11.137046','139','CT-001 - Cartucho 500ml',3,'',15,2),(126,'2026-10-19 00:40:11.137059','132','CU-002 - Cucharas de Sopa',3,'',15,2),(127,'2026-10-19 00:40:11.137073','131','CU-001 - Tenedores de Mesa',3,'',15,2),(128,'2026-10-19 00:40:11.137085','127','PA-001 - Papel Aluminio 40cm',3,'',15,2),(129,'2026-10-19 00:40:11.137098','128','PA-002 - Papel Aluminio 45cm',3,'',15,2),(130,'2026-10-19 00:40:11.137110','136','PL-002 - Platos Desechables 10',3,'',15,2),(131,'2026-10-19 00:40:11.137123','135','PL-001 - Platos Desechables 9',3,'',15,2),(132,'2026-10-19 00:40:11.137135','137','VA-001 - Vasos Plásticos 12oz',3,'',15,2),(133,'2026-10-19 00:40:11.137147','138','VA-002 - Vasos Plásticos 16oz',3,'',15,2),(134,'2026-10-19 00:40:50.012657','124','7 595288 000024 - Bolsa Hermética SLIDER MEDIANA (20U)',2,'[{\"changed\": {\"fields\": [\"SKU\", \"Precio sugerido al consumidor\"]}}]',15,2),(135,'2026-10-19 00:43:05.500979','141','BX-S15 - Bolsa Hermética SLIDER GRANDE (15U)',1,'[{\"added\": {}}]',15,2),(136,'2026-10-19 01:10:23.299094','124','BX-S20 - Bolsa Hermética SLIDER MEDIANA (20U)',2,'[{\"changed\": {\"fields\": [\"SKU\"]}}]',15,2),(137,'2026-10-19 01:12:22.929610','142','BX-S30 - Bolsa Hermética SLIDER GRANDE (30U)',1,'[{\"added\": {}}]',15,2),(138,'2026-10-19 01:13:43.897567','143','BX-S40 - Bolsa Hermética SLIDER GRANDE (40U)',1,'[{\"added\": {}}]',15,2),(139,'2026-10-19 01:15:47.928614','144','BX-D24 - Bolsa Hermética DOBLE CIERRE MEDIANA (24U)',1,'[{\"added\": {}}]',15,2),(140,'2026-10-19 01:17:29.681004','145','BX-D19 - Bolsa Hermética DOBLE CIERRE GRANDE (19U)',1,'[{\"added\": {}}]',15,2),(141,'2026-10-19 01:19:21.827448','146','BX-D10 - Bolsa Hermética DOBLE CIERRE JUMBO (10U)',1,'[{\"added\": {}}]',15,2),(142,'2026-10-19 01:21:21.849059','147','BX-D38 - Bolsa Hermética DOBLE CIERRE GRANDE (38U)',1,'[{\"added\": {}}]',15,2),(143,'2026-10-19 01:23:13.544285','148','BX-D48 - Bolsa Hermética DOBLE CIERRE MEDIANA (48U)',1,'[{\"added\": {}}]',15,2),(144,'2026-10-19 01:26:05.304118','149','BX-A20 - Bolsa Hermética CIERRE ANCHO GRANDE (20U)',1,'[{\"added\": {}}]',15,2),(145,'2026-10-19 01:27:59.943752','145','BX-D19 - Bolsa Hermética DOBLE CIERRE GRANDE (19U)',2,'[{\"changed\": {\"fields\": [\"Unidades por caja\"]}}]',15,2),(146,'2026-10-19 01:30:14.690083','150','BX-A25 - Bolsa Hermética CIERRE ANCHO MEDIANA (25U)',1,'[{\"added\": {}}]',15,2),(147,'2026-10-19 01:31:34.767531','151','BX-W50 - Bolsa Hermética SANDWICH (50U)',1,'[{\"added\": {}}]',15,2),(148,'2026-10-19 01:33:29.717670','152','BX-W100 - Bolsa Hermética SANDWICH (100U)',1,'[{\"added\": {}}]',15,2),(149,'2026-10-19 01:35:13.572285','153','BX-K40 - Bolsa Hermética SNACK (40U)',1,'[{\"added\": {}}]',15,2),(150,'2026-10-19 01:37:20.887649','154','BX-PA25 - Papel Aluminio 25 SQFT',1,'[{\"added\": {}}]',15,2),(151,'2026-10-19 01:40:40.497234','155','BX-AL50 - Papel Aluminio 50 SQFT',1,'[{\"added\": {}}]',15,2),(152,'2026-10-19 01:43:00.148593','156','BX-AL75 - Papel Aluminio 75 SQFT',1,'[{\"added\": {}}]',15,2),(153,'2026-10-19 01:44:42.209571','157','BX-PA16EF - Papel Aluminio EXTRA-FUERTE 16FT',1,'[{\"added\": {}}]',15,2),(154,'2026-10-19 01:46:11.230146','158','BX-PA16 - Papel Aluminio 16FT',1,'[{\"added\": {}}]',15,2),(155,'2026-10-20 12:57:31.661175','159','BX-BNFP - Bolsa Negra 18x18 FLAT PEQUEÑA',1,'[{\"added\": {}}]',15,2),(156,'2026-10-20 12:59:31.327393','160','BX-BBFP - Bolsa Blanca 18x18 FLAT PEQUEÑA',1,'[{\"added\": {}}]',15,2),(157,'2026-10-20 13:02:33.961326','161','BX-BNFM - Bolsa Negra 22x24 FLAT MEDIANA',1,'[{\"added\": {}}]',15,2),(158,'2026-10-20 13:04:45.168993','162','BX-BNFG - Bolsa Negra 23.5\"×30\" FLAT GRANDE',1,'[{\"added\": {}}]',15,2),(159,'2026-10-20 13:06:12.151537','163','BX-BNFXG - Bolsa Negra 32\"×40\" FLAT GIGANTE',1,'[{\"added\": {}}]',15,2),(160,'2026-10-20 13:07:59.820705','164','BX-BNFXL - Bolsa Negra FLAT JUMBO',1,'[{\"added\": {}}]',15,2),(161,'2026-10-20 13:09:24.432816','164','BX-BNFXL - Bolsa Negra FLAT JUMBO',2,'[{\"changed\": {\"fields\": [\"Precio por caja\", \"Precio por unidad\", \"Precio sugerido al consumidor\"]}}]',15,2),(162,'2026-10-20 13:13:43.465871','165','BX-BNAP - Bolsa Negra Agarradera Pequeña',1,'[{\"added\": {}}]',15,2),(163,'2026-10-20 13:14:44.513778','166','BX-BBAP - Bolsa Blanca Agarradera Pequeña',1,'[{\"added\": {}}]',15,2),(164,'2026-10-20 13:16:51.932460','167','BX-BNAM - Bolsa Negra Agarradera Mediana',1,'[{\"added\": {}}]',15,2),(165,'2026-10-20 13:18:11.315778','168','BX-BNAG - Bolsa Negra Agarradera Grande',1,'[{\"added\": {}}]',15,2),(166,'2026-10-20 13:19:23.012221','169','BX-BNAXG - Bolsa Negra Agarradera Gigante',1,'[{\"added\": {}}]',15,2),(167,'2026-10-20 13:21:46.870023','170','BX-CT01 - Tenedor Transparente',1,'[{\"added\": {}}]',15,2),(168,'2026-10-20 13:23:08.993459','171','BX-CT03 - Cuchara Transparente',1,'[{\"added\": {}}]',15,2),(169,'2026-10-20 13:24:28.815167','172','Bx-CB01 - Tenedor Blanco',1,'[{\"added\": {}}]',15,2),(170,'2026-10-20 13:25:40.168224','173','BX-CT02 - Cuchillo Transparente',1,'[{\"added\": {}}]',15,2),(171,'2026-10-20 13:26:51.065906','174','BX-CB02 - Cuchillo Blanco',1,'[{\"added\": {}}]',15,2),(172,'2026-10-20 13:28:24.840330','175','Bx-CB03 - Cuchara Blanco',1,'[{\"added\": {}}]',15,2),(173,'2026-10-20 13:32:17.310500','168','BX-BNAG - Bolsa Negra Agarradera Grande',2,'[{\"changed\": {\"fields\": [\"Imagen\"]}}]',15,2),(174,'2026-10-20 13:34:38.129049','176','BX-PL07 - Bwol Blanco 7',1,'[{\"added\": {}}]',15,2),(175,'2026-10-20 13:36:07.745342','177','BX-PL8 - Plato Blanco 8',1,'[{\"added\": {}}]',15,2),(176,'2026-10-20 13:37:31.540196','178','BX-PL9 - Plato Blanco 9 (25U)',1,'[{\"added\": {}}]',15,2),(177,'2026-10-20 13:37:56.402577','177','BX-PL8 - Plato Blanco 8 (25U)',2,'[{\"changed\": {\"fields\": [\"Nombre del producto\"]}}]',15,2),(178,'2026-10-20 13:38:23.196397','176','BX-PL07 - Bwol Blanco 7 (20U)',2,'[{\"changed\": {\"fields\": [\"Nombre del producto\"]}}]',15,2),(179,'2026-10-20 13:39:48.082553','179','BX-PL10 - Bwol Blanco 10 (20U)',1,'[{\"added\": {}}]',15,2),(180,'2026-10-20 13:44:37.436312','180','BX-VB16 - Vasos Blancos 16 ONZ (25U)',1,'[{\"added\": {}}]',15,2),(181,'2026-10-20 13:46:00.338020','181','BX-BV10 - Vasos Blancos 10 ONZ (25U)',1,'[{\"added\": {}}]',15,2),(182,'2026-10-20 13:47:12.921601','182','BX-BV12 - Vasos Blancos 12 ONZ (25U)',1,'[{\"added\": {}}]',15,2),(183,'2026-10-20 13:48:54.382368','183','BX-VT16 - Vasos Transparentes 16 ONZ (25U)',1,'[{\"added\": {}}]',15,2),(184,'2026-10-20 13:50:10.733083','184','BX-VT10 - Vasos Transparentes 10 ONZ (25U)',1,'[{\"added\": {}}]',15,2),(185,'2026-10-20 13:51:23.975186','185','BX-VT12 - Vasos Transparentes 12 ONZ (25U)',1,'[{\"added\": {}}]',15,2),(186,'2026-10-20 13:52:41.305735','186','BX-VD10 - Vasos Transparentes Duros 10 ONZ (25U)',1,'[{\"added\": {}}]',15,2),(187,'2026-10-20 13:54:03.753234','187','BX-VD12 - Vasos Transparentes Duros 12 ONZ (25U)',1,'[{\"added\": {}}]',15,2),(188,'2026-10-20 14:07:33.805607','188','BX-F39 - Cartucho Transparente 3×9 (100U)',1,'[{\"added\": {}}]',15,2),(189,'2026-10-20 14:08:55.534896','189','BX-F510 - Cartucho Transparente 5×10 (100U)',1,'[{\"added\": {}}]',15,2),(190,'2026-10-20 14:11:48.306816','190','BX-F612 - Cartucho Transparente 6×12 (100U)',1,'[{\"added\": {}}]',15,2),(191,'2026-10-20 14:13:09.286357','191','BX-F712 - Cartucho Transparente 7×12 (100U)',1,'[{\"added\": {}}]',15,2),(192,'2026-10-20 14:15:27.177388','192','BX- F510 - Cartucho Transparente 8×14 (100U)',1,'[{\"added\": {}}]',15,2),(193,'2026-10-20 14:16:28.960866','193','BX-F1015 - Cartucho Transparente 10×15 (100U)',1,'[{\"added\": {}}]',15,2),(194,'2026-10-20 14:20:17.884797','194','PK-BNFP - Media Caja Bolsa Negra FLAT PEQUEÑA',1,'[{\"added\": {}}]',15,2),(195,'2026-10-20 14:20:47.535086','194','PK-BNFP - Media Caja Bolsa Negra FLAT PEQUEÑA',2,'[{\"changed\": {\"fields\": [\"Imagen\"]}}]',15,2),(196,'2026-10-20 23:14:25.795148','195','PK-BBFP - Media Caja Bolsa Blanca FLAT PEQUEÑA',1,'[{\"added\": {}}]',15,2),(197,'2026-10-20 23:16:03.173167','195','PK-BBFP - Media Caja Bolsa Blanca FLAT PEQUEÑA',2,'[{\"changed\": {\"fields\": [\"Imagen\"]}}]',15,2),(198,'2026-10-20 23:37:31.441673','196','PK-BNFM - Media Caja Bolsa Negra FLAT MEDIANA',1,'[{\"added\": {}}]',15,2),(199,'2026-10-20 23:38:59.343669','197','PK-BNFG - Media Caja Bolsa Negra FLAT GRANDE',1,'[{\"added\": {}}]',15,2),(200,'2026-10-20 23:42:36.938660','198','PK-BNFXG - Media Caja Bolsa Negra FLAT GIGANTE',1,'[{\"added\": {}}]',15,2),(201,'2026-10-20 23:43:33.530351','199','PK-BNFXL - Media Caja Bolsa Negra FLAT JUMBO',1,'[{\"added\": {}}]',15,2),(202,'2026-10-20 23:44:52.800140','200','PK-BNAP - Media Caja Bolsa Agarradera Pequeña',1,'[{\"added\": {}}]',15,2),(203,'2026-10-20 23:46:13.078792','201','PK-BBAP - Media Caja Bolsa Blanca Agarradera Pequeña',1,'[{\"added\": {}}]',15,2),(204,'2026-10-20 23:47:16.234458','202','PK-BNAM - Media Caja Bolsa Negra Agarradera Mediana',1,'[{\"added\": {}}]',15,2),(205,'2026-10-20 23:48:16.226624','203','PK-BNAG - Media Caja Bolsa Negra Agarradera Grande',1,'[{\"added\": {}}]',15,2),(206,'2026-10-20 23:49:23.497621','204','PK-BNAXG - Media Caja Bolsa Negra Agarradera Gigante',1,'[{\"added\": {}}]',15,2),(207,'2026-10-20 23:51:44.952253','205','PK-S20 - Media Caja SLIDER MEDIANA (20U)',1,'[{\"added\": {}}]',15,2),(208,'2026-10-20 23:52:51.991673','206','PK-S15 - Media Caja SLIDER GRANDE (12U)',1,'[{\"added\": {}}]',15,2),(209,'2026-10-20 23:54:33.586473','207','PK-DC19 - Media Caja SLIDER Doble Cierre Grande (19U)',1,'[{\"added\": {}}]',15,2),(210,'2026-10-20 23:56:08.523569','208','PK-DC24 - Media Caja SLIDER Doble Cierre Mediano (24U)',1,'[{\"added\": {}}]',15,2),(211,'2026-10-20 23:57:42.734041','209','PK-CA25 - Media Caja SLIDER Cierre Ancho Mediano (25U)',1,'[{\"added\": {}}]',15,2),(212,'2026-10-21 00:01:59.262682','210','PK-CA20 - Media Caja SLIDER Cierre Ancho Grande (20U)',1,'[{\"added\": {}}]',15,2),(213,'2026-10-21 00:03:24.289096','211','PK-W50 - Media Caja SLIDER SANDWICH (50U)',1,'[{\"added\": {}}]',15,2),(214,'2026-10-21 00:08:52.907769','212','PK-CT03 - Media Caja Cuchara Transparente (25U)',1,'[{\"added\": {}}]',15,2),(215,'2026-10-21 00:09:40.739331','213','PK-CB03 - Media Caja Cuchara Blanca (25U)',1,'[{\"added\": {}}]',15,2),(216,'2026-10-21 00:10:43.413204','214','PK-CT01 - Media Caja Tenedor Transparente (25U)',1,'[{\"added\": {}}]',15,2),(217,'2026-10-21 00:11:11.666137','203','PK-BNAG - Media Caja Bolsa Negra Agarradera Grande',2,'[{\"changed\": {\"fields\": [\"\\u00bfPermite venta por media caja?\"]}}]',15,2),(218,'2026-10-21 00:12:27.877113','215','PK-CB01 - Media Caja Tenedor Blanco (25U)',1,'[{\"added\": {}}]',15,2),(219,'2026-10-21 00:16:41.007786','216','PK-VB16 - Media Caja Vasos Blancos 16 ONZ (25U)',1,'[{\"added\": {}}]',15,2),(220,'2026-10-21 00:17:44.255721','217','PK-VB10 - Media Caja Vasos Blancos 10 ONZ (25U)',1,'[{\"added\": {}}]',15,2),(221,'2026-10-21 00:18:55.619115','218','PK-VB12 - Media Caja Vasos Blancos 12 ONZ (25U)',1,'[{\"added\": {}}]',15,2),(222,'2026-10-21 00:21:40.282466','219','PK-VT16 - Media Caja Vasos Transparentes 16 ONZ (25U)',1,'[{\"added\": {}}]',15,2),(223,'2026-10-21 00:22:53.655710','220','PK-VT10 - Media Caja Vasos Transparentes 10 ONZ (25U)',1,'[{\"added\": {}}]',15,2),(224,'2026-10-21 00:24:16.311792','221','PK-VT12 - Media Caja Vasos Transparentes 12 ONZ (25U)',1,'[{\"added\": {}}]',15,2),(225,'2026-10-21 00:25:32.063200','222','PK-VD10 - Media Caja Vasos Transparentes Duros 10 ONZ (25U)',1,'[{\"added\": {}}]',15,2),(226,'2026-10-21 00:26:51.837754','223','PK-VD12 - Media Caja Vasos Transparentes Duros 12 ONZ (25U)',1,'[{\"added\": {}}]',15,2),(227,'2026-10-21 00:29:05.039779','224','BX-PAL75 - Media Caja Papel Aluminio 16 FT',1,'[{\"added\": {}}]',15,2),(228,'2026-10-21 00:31:00.167704','224','BX-PAL75 - Media Caja Papel Aluminio 16 FT',2,'[{\"changed\": {\"fields\": [\"C\\u00f3digo de barras\"]}}]',15,2),(229,'2026-10-21 00:32:46.020067','225','BLX-PA25 - Media Caja Papel Aluminio 25 FT',1,'[{\"added\": {}}]',15,2),(230,'2026-10-21 00:35:47.323188','226','BLX-PA50 - Media Caja Papel Aluminio 50 FT',1,'[{\"added\": {}}]',15,2),(231,'2026-10-21 00:37:42.048566','227','BLX-PA16EF - Media Caja Papel Aluminio EXTRA-FUERTE 16 FT',1,'[{\"added\": {}}]',15,2);
/*!40000 ALTER TABLE `django_admin_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_content_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `model` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_content_type`
--

LOCK TABLES `django_content_type` WRITE;
/*!40000 ALTER TABLE `django_content_type` DISABLE KEYS */;
INSERT INTO `django_content_type` VALUES (1,'admin','logentry'),(3,'auth','group'),(2,'auth','permission'),(4,'auth','user'),(16,'catalogo','categoria'),(13,'catalogo','clienteb2b'),(14,'catalogo','lineapedidob2b'),(12,'catalogo','pedidob2b'),(15,'catalogo','producto'),(5,'contenttypes','contenttype'),(7,'facturacion','configuracionnegocio'),(11,'facturacion','contadorordencompra'),(8,'facturacion','contadorserie'),(9,'facturacion','factura'),(10,'facturacion','lineafactura'),(6,'sessions','session');
/*!40000 ALTER TABLE `django_content_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_migrations`
--

DROP TABLE IF EXISTS `django_migrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_migrations` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `app` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=33 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_migrations`
--

LOCK TABLES `django_migrations` WRITE;
/*!40000 ALTER TABLE `django_migrations` DISABLE KEYS */;
INSERT INTO `django_migrations` VALUES (1,'contenttypes','0001_initial','2026-10-04 16:17:53.888155'),(2,'auth','0001_initial','2026-10-04 16:17:54.806680'),(3,'admin','0001_initial','2026-10-04 16:17:55.037869'),(4,'admin','0002_logentry_remove_auto_add','2026-10-04 16:17:55.048794'),(5,'admin','0003_logentry_add_action_flag_choices','2026-10-04 16:17:55.068930'),(6,'contenttypes','0002_remove_content_type_name','2026-10-04 16:17:55.226648'),(7,'auth','0002_alter_permission_name_max_length','2026-10-04 16:17:55.339497'),(8,'auth','0003_alter_user_email_max_length','2026-10-04 16:17:55.403985'),(9,'auth','0004_alter_user_username_opts','2026-10-04 16:17:55.423898'),(10,'auth','0005_alter_user_last_login_null','2026-10-04 16:17:55.523174'),(11,'auth','0006_require_contenttypes_0002','2026-10-04 16:17:55.528225'),(12,'auth','0007_alter_validators_add_error_messages','2026-10-04 16:17:55.537561'),(13,'auth','0008_alter_user_username_max_length','2026-10-04 16:17:55.625958'),(14,'auth','0009_alter_user_last_name_max_length','2026-10-04 16:17:55.715968'),(15,'auth','0010_alter_group_name_max_length','2026-10-04 16:17:55.742429'),(16,'auth','0011_update_proxy_permissions','2026-10-04 16:17:55.752554'),(17,'auth','0012_alter_user_first_name_max_length','2026-10-04 16:17:55.843705'),(18,'facturacion','0001_initial','2026-10-04 16:17:56.054088'),(19,'facturacion','0002_cambios_cliente','2026-10-04 16:17:56.487724'),(20,'facturacion','0003_contadorordencompra_remove_factura_dias_credito_and_more','2026-10-04 16:17:56.794447'),(21,'facturacion','0004_lineafactura_cobrar_por_and_more','2026-10-04 16:17:56.959909'),(22,'facturacion','0005_alter_configuracionnegocio_color_barra_factura','2026-10-04 16:17:56.966583'),(23,'sessions','0001_initial','2026-10-04 16:17:57.020665'),(24,'catalogo','0001_initial','2026-10-04 17:17:58.629353'),(25,'facturacion','0006_lineafactura_producto','2026-10-04 17:17:58.730212'),(27,'facturacion','0007_lineafactura_precio_unidad_and_more','2026-10-05 16:48:18.405633'),(28,'facturacion','0008_alter_lineafactura_precio_unidad','2026-10-05 16:48:18.517384'),(29,'catalogo','0002_remove_lineapedidob2b_cantidad_cajas_and_more','2026-10-16 12:48:27.619474'),(30,'catalogo','0003_producto_permite_media_caja_and_more','2026-10-16 13:01:41.361585'),(31,'catalogo','0004_producto_codigo_barras','2026-10-19 00:21:46.524283'),(32,'catalogo','0005_producto_precio_consumidor','2026-10-19 00:38:46.826141');
/*!40000 ALTER TABLE `django_migrations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_session` (
  `session_key` varchar(40) COLLATE utf8mb4_unicode_ci NOT NULL,
  `session_data` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_session`
--

LOCK TABLES `django_session` WRITE;
/*!40000 ALTER TABLE `django_session` DISABLE KEYS */;
INSERT INTO `django_session` VALUES ('d761iyrzrugb8jzbb1nj719qike7fxjc','.eJxVjDkOwjAQAP-yNbLWN0lJnzdYm_UaB5Aj5agQf0eRUkA7M5o3JNq3mvZVljRl6MHA5ZeNxE9ph8gPavdZ8dy2ZRrVkajTrmqYs7xuZ_s3qLRW6OHKOviR0EYS1EFKxBIDG9FskNl5R7a46JGdZimUsWNkErE5l85Z-HwB7ZM4pw:1xDQL9:B7-iwpQlNQNIg4sgv2TRUIwUldwjtw5Vw1xlSw1ZyKw','2026-10-18 17:49:35.917421'),('l7n4moj24u8ed9rqo4xe6eupa97oi1ot','.eJxVjDkOwjAQAP-yNbLWN0lJnzdYm_UaB5Aj5agQf0eRUkA7M5o3JNq3mvZVljRl6MHA5ZeNxE9ph8gPavdZ8dy2ZRrVkajTrmqYs7xuZ_s3qLRW6OHKOviR0EYS1EFKxBIDG9FskNl5R7a46JGdZimUsWNkErE5l85Z-HwB7ZM4pw:1xJJDz:_0IoNkJ-plsP2r9Ru3grgxs54MV5trHFbBxRZtBqQdk','2026-11-03 23:26:31.306443');
/*!40000 ALTER TABLE `django_session` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `facturacion_configuracionnegocio`
--

DROP TABLE IF EXISTS `facturacion_configuracionnegocio`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `facturacion_configuracionnegocio` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `empresa_nombre` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `empresa_ruc` varchar(40) COLLATE utf8mb4_unicode_ci NOT NULL,
  `empresa_direccion` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `empresa_correo` varchar(254) COLLATE utf8mb4_unicode_ci NOT NULL,
  `empresa_telefono` varchar(60) COLLATE utf8mb4_unicode_ci NOT NULL,
  `logo` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `color_principal` varchar(7) COLLATE utf8mb4_unicode_ci NOT NULL,
  `datos_bancarios` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `actualizado` datetime(6) NOT NULL,
  `color_barra_factura` varchar(7) COLLATE utf8mb4_unicode_ci NOT NULL,
  `color_tabla` varchar(7) COLLATE utf8mb4_unicode_ci NOT NULL,
  `notas_predeterminadas` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `mostrar_ruc` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `facturacion_configuracionnegocio`
--

LOCK TABLES `facturacion_configuracionnegocio` WRITE;
/*!40000 ALTER TABLE `facturacion_configuracionnegocio` DISABLE KEYS */;
INSERT INTO `facturacion_configuracionnegocio` VALUES (1,'BENSULCO DISTRIBUTION, S.A.','155727293-2-2022 DV:42','DON BOSCO, JUAN DIAZ, PANAMÁ.','info@bensulco.com','+507 6577-0662','logos/Logo_BensulcoDistri.jpg','#3a0088','','2026-10-15 15:32:51.925955','#5b3a9e','#3a0088','',1);
/*!40000 ALTER TABLE `facturacion_configuracionnegocio` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `facturacion_contadorordencompra`
--

DROP TABLE IF EXISTS `facturacion_contadorordencompra`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `facturacion_contadorordencompra` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `anio` int unsigned NOT NULL,
  `ultimo_numero` int unsigned NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `anio` (`anio`),
  CONSTRAINT `facturacion_contadorordencompra_chk_1` CHECK ((`anio` >= 0)),
  CONSTRAINT `facturacion_contadorordencompra_chk_2` CHECK ((`ultimo_numero` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `facturacion_contadorordencompra`
--

LOCK TABLES `facturacion_contadorordencompra` WRITE;
/*!40000 ALTER TABLE `facturacion_contadorordencompra` DISABLE KEYS */;
INSERT INTO `facturacion_contadorordencompra` VALUES (1,2026,11);
/*!40000 ALTER TABLE `facturacion_contadorordencompra` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `facturacion_contadorserie`
--

DROP TABLE IF EXISTS `facturacion_contadorserie`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `facturacion_contadorserie` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `anio` int unsigned NOT NULL,
  `ultimo_numero` int unsigned NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `anio` (`anio`),
  CONSTRAINT `facturacion_contadorserie_chk_1` CHECK ((`anio` >= 0)),
  CONSTRAINT `facturacion_contadorserie_chk_2` CHECK ((`ultimo_numero` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `facturacion_contadorserie`
--

LOCK TABLES `facturacion_contadorserie` WRITE;
/*!40000 ALTER TABLE `facturacion_contadorserie` DISABLE KEYS */;
INSERT INTO `facturacion_contadorserie` VALUES (1,2026,11);
/*!40000 ALTER TABLE `facturacion_contadorserie` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `facturacion_factura`
--

DROP TABLE IF EXISTS `facturacion_factura`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `facturacion_factura` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `numero_serie` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `codigo_verificacion` varchar(12) COLLATE utf8mb4_unicode_ci NOT NULL,
  `fecha` date NOT NULL,
  `cliente_nombre` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `cliente_ruc` varchar(40) COLLATE utf8mb4_unicode_ci NOT NULL,
  `cliente_direccion` varchar(250) COLLATE utf8mb4_unicode_ci NOT NULL,
  `cliente_telefono` varchar(60) COLLATE utf8mb4_unicode_ci NOT NULL,
  `cliente_correo` varchar(254) COLLATE utf8mb4_unicode_ci NOT NULL,
  `sucursal` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `orden_compra` varchar(60) COLLATE utf8mb4_unicode_ci NOT NULL,
  `vendedor` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `condicion_pago` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `portes` decimal(14,2) NOT NULL,
  `subtotal` decimal(14,2) NOT NULL,
  `descuento_total` decimal(14,2) NOT NULL,
  `base_gravada` decimal(14,2) NOT NULL,
  `base_exenta` decimal(14,2) NOT NULL,
  `itbms` decimal(14,2) NOT NULL,
  `total` decimal(14,2) NOT NULL,
  `estado` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
  `fecha_creacion` datetime(6) NOT NULL,
  `fecha_anulacion` datetime(6) DEFAULT NULL,
  `notas` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `mostrar_ruc` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `numero_serie` (`numero_serie`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `facturacion_factura`
--

LOCK TABLES `facturacion_factura` WRITE;
/*!40000 ALTER TABLE `facturacion_factura` DISABLE KEYS */;
INSERT INTO `facturacion_factura` VALUES (1,'FAC-2026-0001','UET7NXHHNSQF','2026-08-05','SUPERMERCADO EL PROGRESO S.A.','1-2345678-90-123','Avenida Balboa, Ciudad de Panamá','+507 200-1234','compras@elprogreso.example','Sucursal Centro','OC-2026-0001','María Pérez','credito',0.00,29.50,0.00,29.50,0.00,2.07,31.57,'emitida','2026-10-04 16:51:46.862114',NULL,'',1),(4,'FAC-2026-0004','6PW5VWU9USBP','2026-10-03','DISTRIBUIDORA DEL ISTMO S.A.','1-9876543-21-000','Vía España, Panamá Viejo','+507 300-5566','pagos@istmo.example','Sucursal Cerro Viento','OC-2026-0004','Luis Batista','contado',0.00,21.40,0.00,21.40,0.00,1.50,22.90,'anulada','2026-10-04 16:51:46.887273','2026-10-04 16:51:46.889691','El cliente devolvió la mercancia.',1),(5,'FAC-2026-0005','QPULRW7GVCSJ','2026-10-20','SUPERMERCADO EL PROGRESO S.A.','1-2345678-90-123','Avenida Balboa, Ciudad de Panamá','+507 200-1234','compras@elprogreso.example','Sucursal Centro','OC-2026-0005','María Pérez','contado',0.00,125.30,0.00,125.30,0.00,8.77,134.07,'emitida','2026-10-04 16:51:46.895211',NULL,'Entrega a domicilio en menos de 24 horas.\nGracias por preferirnos.',1),(6,'FAC-2026-0006','JHMXB3EXXZEH','2026-10-22','DISTRIBUIDORA DEL ISTMO S.A.','1-9876543-21-000','Vía España, Panamá Viejo','+507 300-5566','pagos@istmo.example','Sucursal Cerro Viento','OC-2026-0006','Luis Batista','credito',0.00,617.20,0.00,617.20,0.00,43.20,660.40,'emitida','2026-10-04 16:51:46.908529',NULL,'Pedido al por mayor. Entrega en el almacen del cliente.\nRevisar el empaque antes de firmar la recepcion.',1),(7,'FAC-2026-0007','LTA43NEF5MQ6','2026-10-04','DISTRIBUIDORA DEL ISTMO S.A.','1-9876543-21-000','Vía España, Panamá Viejo','+507 300-5566','pagos@istmo.example','','OC-2026-0007','','credito',0.00,14.45,0.00,14.45,0.00,1.01,15.46,'emitida','2026-10-04 17:45:34.595139',NULL,'Pedido de prueba para conversión a factura.',1),(8,'FAC-2026-0008','APYMPXSU6E4B','2026-10-13','Javier Domínguez','8-102-456','Chorrerita','6300-7166','Javier1001@gmail.com','Tienda','OC-2026-0008','Jesús Moreno','contado',0.00,172.90,0.00,172.90,0.00,12.10,185.00,'anulada','2026-10-13 21:37:39.707919','2026-10-15 14:51:51.779679','Conserve esta factura y preséntela para cualquier reclamo.\r\nGracias por su compra.',1),(9,'FAC-2026-0009','GQM75LQJRVJ3','2026-10-15','Javier Domínguez','8-102-456','','6300-7166','Javier1001@gmail.com','Tienda','OC-2026-0009','Jesús Moreno','contado',0.00,87.02,0.00,87.02,0.00,6.09,93.11,'anulada','2026-10-15 14:45:35.451694','2026-10-15 14:52:08.091460','Conserve esta factura y preséntela para cualquier reclamo.\r\nGracias por su compra.',1),(10,'FAC-2026-0010','DSVBTREVSB8P','2026-10-15','Jesús Moreno','8-102-456','','6300-7166','Javier1001@gmail.com','Tienda','OC-2026-0010','Jesús Moreno','contado',0.00,101.02,0.00,101.02,0.00,7.07,108.09,'emitida','2026-10-15 14:59:51.470891',NULL,'IRVING ES GAY',1),(11,'FAC-2026-0011','PSBVLPF98B9Y','2026-10-15','M/S Prolog','8-102-456','Farallón','6300-7166','Javier1001@gmail.com','Tienda','OC-2026-0011','Jesús Moreno','contado',0.00,262.94,0.00,262.94,0.00,18.41,281.35,'emitida','2026-10-15 15:42:11.821306',NULL,'',1);
/*!40000 ALTER TABLE `facturacion_factura` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `facturacion_lineafactura`
--

DROP TABLE IF EXISTS `facturacion_lineafactura`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `facturacion_lineafactura` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `orden` int unsigned NOT NULL,
  `descripcion` varchar(300) COLLATE utf8mb4_unicode_ci NOT NULL,
  `codigo_barras` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `categoria` varchar(120) COLLATE utf8mb4_unicode_ci NOT NULL,
  `cantidad` decimal(14,2) NOT NULL,
  `precio_unitario` decimal(14,2) NOT NULL,
  `descuento_pct` decimal(6,2) NOT NULL,
  `gravada` tinyint(1) NOT NULL,
  `monto` decimal(14,2) NOT NULL,
  `factura_id` bigint NOT NULL,
  `cobrar_por` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
  `unidades_por_caja` int unsigned NOT NULL,
  `producto_id` bigint DEFAULT NULL,
  `precio_unidad` decimal(14,2) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `linea_factura_orden_unico` (`factura_id`,`orden`),
  KEY `facturacion_lineafac_producto_id_66271b99_fk_catalogo_` (`producto_id`),
  CONSTRAINT `facturacion_lineafac_factura_id_633e103a_fk_facturaci` FOREIGN KEY (`factura_id`) REFERENCES `facturacion_factura` (`id`),
  CONSTRAINT `facturacion_lineafac_producto_id_66271b99_fk_catalogo_` FOREIGN KEY (`producto_id`) REFERENCES `catalogo_producto` (`id`),
  CONSTRAINT `facturacion_lineafactura_chk_1` CHECK ((`orden` >= 0)),
  CONSTRAINT `facturacion_lineafactura_chk_2` CHECK ((`unidades_por_caja` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=87 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `facturacion_lineafactura`
--

LOCK TABLES `facturacion_lineafactura` WRITE;
/*!40000 ALTER TABLE `facturacion_lineafactura` DISABLE KEYS */;
INSERT INTO `facturacion_lineafactura` VALUES (1,1,'Azúcar refinada 2 kg','750164632398','Abarrotes',2.00,3.40,0.00,1,6.80,1,'unidad',1,NULL,0.00),(2,2,'Leche entera 1 L','750175834722','Lácteos',3.00,1.95,0.00,1,5.85,1,'unidad',1,NULL,0.00),(3,3,'Queso blanco 500 g','750168661177','Lácteos',1.00,5.60,0.00,1,5.60,1,'unidad',1,NULL,0.00),(4,4,'Jamón cocido 250 g','750150303712','Carnes',2.00,4.10,0.00,1,8.20,1,'unidad',1,NULL,0.00),(5,5,'Pan dulce','750177713417','Panadería',3.00,0.60,0.00,1,1.80,1,'unidad',1,NULL,0.00),(6,6,'Galletas de soda','750151641979','Panadería',1.00,1.25,0.00,1,1.25,1,'unidad',1,NULL,0.00),(19,1,'Aceite vegetal 900 ml','750176072858','Abarrotes',2.00,4.85,0.00,1,9.70,4,'unidad',1,NULL,0.00),(20,2,'Leche entera 1 L','750175834722','Lácteos',6.00,1.95,0.00,1,11.70,4,'unidad',1,NULL,0.00),(21,1,'Aceite vegetal 900 ml','750176072858','Abarrotes',1.00,4.85,0.00,1,4.85,5,'unidad',1,NULL,0.00),(22,2,'Arroz precocido 5 lb','750101356859','Abarrotes',2.00,6.20,0.00,1,12.40,5,'unidad',1,NULL,0.00),(23,3,'Azúcar refinada 2 kg','750164632398','Abarrotes',3.00,3.40,0.00,1,10.20,5,'unidad',1,NULL,0.00),(24,4,'Leche entera 1 L','750175834722','Lácteos',4.00,1.95,0.00,1,7.80,5,'unidad',1,NULL,0.00),(25,5,'Queso blanco 500 g','750168661177','Lácteos',1.00,5.60,0.00,1,5.60,5,'unidad',1,NULL,0.00),(26,6,'Jamón cocido 250 g','750150303712','Carnes',2.00,4.10,0.00,1,8.20,5,'unidad',1,NULL,0.00),(27,7,'Pan dulce','750177713417','Panadería',3.00,0.60,0.00,1,1.80,5,'unidad',1,NULL,0.00),(28,8,'Galletas de soda','750151641979','Panadería',4.00,1.25,0.00,1,5.00,5,'unidad',1,NULL,0.00),(29,9,'Jabón de ropa 3 L','750138627819','Limpieza',1.00,5.90,0.00,1,5.90,5,'unidad',1,NULL,0.00),(30,10,'Cloro desinfectante 2 L','750143157194','Limpieza',2.00,2.35,0.00,1,4.70,5,'unidad',1,NULL,0.00),(31,11,'Detergente en polvo 5 kg','750188460151','Limpieza',3.00,9.75,0.00,1,29.25,5,'unidad',1,NULL,0.00),(32,12,'Papel higiénico 12 rollos','750192310290','Limpieza',4.00,7.40,0.00,1,29.60,5,'unidad',1,NULL,0.00),(33,1,'Aceite vegetal 900 ml','750176072858','Abarrotes',1.00,4.85,0.00,1,4.85,6,'unidad',1,NULL,0.00),(34,2,'Arroz precocido 5 lb','750101356859','Abarrotes',2.00,6.20,0.00,1,12.40,6,'unidad',1,NULL,0.00),(35,3,'Azúcar refinada 2 kg','750164632398','Abarrotes',3.00,3.40,0.00,1,10.20,6,'unidad',1,NULL,0.00),(36,4,'Leche entera 1 L','750175834722','Lácteos',4.00,1.95,0.00,1,7.80,6,'unidad',1,NULL,0.00),(37,5,'Queso blanco 500 g','750168661177','Lácteos',5.00,5.60,0.00,1,28.00,6,'unidad',1,NULL,0.00),(38,6,'Jamón cocido 250 g','750150303712','Carnes',1.00,4.10,0.00,1,4.10,6,'unidad',1,NULL,0.00),(39,7,'Pan dulce','750177713417','Panadería',2.00,0.60,0.00,1,1.20,6,'unidad',1,NULL,0.00),(40,8,'Galletas de soda','750151641979','Panadería',3.00,1.25,0.00,1,3.75,6,'unidad',1,NULL,0.00),(41,9,'Jabón de ropa 3 L','750138627819','Limpieza',4.00,5.90,0.00,1,23.60,6,'unidad',1,NULL,0.00),(42,10,'Cloro desinfectante 2 L','750143157194','Limpieza',5.00,2.35,0.00,1,11.75,6,'unidad',1,NULL,0.00),(43,11,'Detergente en polvo 5 kg','750188460151','Limpieza',1.00,9.75,0.00,1,9.75,6,'unidad',1,NULL,0.00),(44,12,'Papel higiénico 12 rollos','750192310290','Limpieza',2.00,7.40,0.00,1,14.80,6,'unidad',1,NULL,0.00),(45,13,'Café molido 500 g','750188052719','Bebidas',3.00,7.90,0.00,1,23.70,6,'unidad',1,NULL,0.00),(46,14,'Jugo de naranja 1 L','750109261274','Bebidas',4.00,2.10,0.00,1,8.40,6,'unidad',1,NULL,0.00),(47,15,'Agua mineral 1.5 L','750113560579','Bebidas',5.00,1.15,0.00,1,5.75,6,'unidad',1,NULL,0.00),(48,16,'Guantes de nitrilo 100','750112334136','Varios',1.00,6.50,0.00,1,6.50,6,'unidad',1,NULL,0.00),(49,17,'Pilas AA 4','750153215926','Varios',2.00,3.20,0.00,1,6.40,6,'unidad',1,NULL,0.00),(50,18,'Fósforos caja 12','750160032484','Varios',3.00,1.05,0.00,1,3.15,6,'unidad',1,NULL,0.00),(51,19,'Bolsas plásticas medianas 100','750152670444','Limpieza',4.00,30.00,0.00,1,120.00,6,'caja',100,NULL,0.00),(52,20,'Papel aluminio 24 und','750178603643','Abarrotes',5.00,12.00,0.00,1,2.50,6,'unidad',24,NULL,0.00),(53,21,'Aceite vegetal 900 ml (parte 2)','750195074401','Abarrotes',1.00,4.85,0.00,1,4.85,6,'unidad',1,NULL,0.00),(54,22,'Arroz precocido 5 lb (parte 2)','750181604458','Abarrotes',2.00,6.20,0.00,1,12.40,6,'unidad',1,NULL,0.00),(55,23,'Azúcar refinada 2 kg (parte 2)','750180854895','Abarrotes',3.00,3.40,0.00,1,10.20,6,'unidad',1,NULL,0.00),(56,24,'Leche entera 1 L (parte 2)','750160343245','Lácteos',4.00,1.95,0.00,1,7.80,6,'unidad',1,NULL,0.00),(57,25,'Queso blanco 500 g (parte 2)','750119415206','Lácteos',5.00,5.60,0.00,1,28.00,6,'unidad',1,NULL,0.00),(58,26,'Jamón cocido 250 g (parte 2)','750162962949','Carnes',1.00,4.10,0.00,1,4.10,6,'unidad',1,NULL,0.00),(59,27,'Pan dulce (parte 2)','750113642781','Panadería',2.00,0.60,0.00,1,1.20,6,'unidad',1,NULL,0.00),(60,28,'Galletas de soda (parte 2)','750199283846','Panadería',3.00,1.25,0.00,1,3.75,6,'unidad',1,NULL,0.00),(61,29,'Jabón de ropa 3 L (parte 2)','750153490418','Limpieza',4.00,5.90,0.00,1,23.60,6,'unidad',1,NULL,0.00),(62,30,'Cloro desinfectante 2 L (parte 2)','750128824051','Limpieza',5.00,2.35,0.00,1,11.75,6,'unidad',1,NULL,0.00),(63,31,'Detergente en polvo 5 kg (parte 2)','750142051946','Limpieza',1.00,9.75,0.00,1,9.75,6,'unidad',1,NULL,0.00),(64,32,'Papel higiénico 12 rollos (parte 2)','750187443795','Limpieza',2.00,7.40,0.00,1,14.80,6,'unidad',1,NULL,0.00),(65,33,'Café molido 500 g (parte 2)','750186670284','Bebidas',3.00,7.90,0.00,1,23.70,6,'unidad',1,NULL,0.00),(66,34,'Jugo de naranja 1 L (parte 2)','750191994371','Bebidas',4.00,2.10,0.00,1,8.40,6,'unidad',1,NULL,0.00),(67,35,'Agua mineral 1.5 L (parte 2)','750120276824','Bebidas',5.00,1.15,0.00,1,5.75,6,'unidad',1,NULL,0.00),(68,36,'Guantes de nitrilo 100 (parte 2)','750152989777','Varios',1.00,6.50,0.00,1,6.50,6,'unidad',1,NULL,0.00),(69,37,'Pilas AA 4 (parte 2)','750153747011','Varios',2.00,3.20,0.00,1,6.40,6,'unidad',1,NULL,0.00),(70,38,'Fósforos caja 12 (parte 2)','750157505397','Varios',3.00,1.05,0.00,1,3.15,6,'unidad',1,NULL,0.00),(71,39,'Bolsas plásticas medianas 100 (parte 2)','750133159299','Limpieza',4.00,30.00,0.00,1,120.00,6,'caja',100,NULL,0.00),(72,40,'Papel aluminio 24 und (parte 2)','750140825158','Abarrotes',5.00,12.00,0.00,1,2.50,6,'unidad',24,NULL,0.00),(73,1,'Aceite vegetal 900 ml','ACE-001','Abarrotes',1.00,4.85,0.00,1,4.85,7,'caja',30,NULL,0.00),(74,2,'Arroz precocido 5 lb','ARR-001','Abarrotes',1.00,6.20,0.00,1,6.20,7,'caja',5,NULL,0.00),(75,3,'Azúcar refinada 2 kg','AZU-001','Abarrotes',1.00,3.40,0.00,1,3.40,7,'caja',2,NULL,0.00),(76,1,'BLIXI® PAPELES ALUMINIO PAPEL ALUMINIO 25 SQFT','','',2.00,30.00,0.00,1,2.50,8,'unidad',23,NULL,1.25),(77,2,'BLIXI BOLSA NEGRA FLAT PEQUEÑA','','',4.00,65.60,0.00,1,3.64,8,'unidad',40,NULL,0.91),(78,3,'BLIXI® TENEDOR TRANSPARENTE','','',4.00,41.69,0.00,1,166.76,8,'caja',48,NULL,0.87),(79,1,'BLIXI® TENEDOR TRANSPARENTE','','',2.00,41.69,0.00,1,83.38,9,'caja',1,NULL,0.87),(80,2,'BLIXI BOLSA NEGRA FLAT PEQUEÑA','','',4.00,65.60,0.00,1,3.64,9,'unidad',1,NULL,0.91),(81,1,'BLIXI® Bolsa Hermética SLIDER MEDIANA','','',4.00,43.54,0.00,1,7.24,10,'unidad',20,NULL,1.81),(82,2,'BLIXI® Bolsa Hermética SLIDER GRANDE','','',2.00,43.54,0.00,1,87.08,10,'caja',15,NULL,1.81),(83,3,'BLIXI® Bolsa Hermética SLIDER GRANDE 30','','',2.00,80.41,0.00,1,6.70,10,'unidad',30,NULL,3.35),(84,1,'BLIXI® Bolsa Hermética SLIDER MEDIANA','7 595288 000024','',2.00,43.54,0.00,1,87.08,11,'caja',24,NULL,1.81),(85,2,'BLIXI BOLSA NEGRA FLAT PEQUEÑA','7 595288 00550','',10.00,65.60,0.00,1,9.10,11,'unidad',80,NULL,0.91),(86,3,'BLIXI® TENEDOR TRANSPARENTE','7 595288 002639','',4.00,41.69,0.00,1,166.76,11,'caja',48,NULL,0.87);
/*!40000 ALTER TABLE `facturacion_lineafactura` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-10-25  9:00:04
