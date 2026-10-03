# FacturaJesus

Aplicacion web de facturacion para Panama: emite facturas en PDF, lleva el
historial, permite duplicar y anular, y publica un codigo de verificacion con
codigo QR. No tiene usuarios ni iniciar sesion: esta pensada para usarse en la
red interna del negocio, detras del servidor web o de una VPN.

Todo el texto de la interfaz, de los PDF y de esta documentacion esta en
espanol de Panama.

## Requisitos

- Python 3.12
- MySQL 8 (opcional: se puede trabajar con SQLite)
- Bibliotecas de MySQL: `sudo apt install default-libmysqlclient-dev build-essential`

## Instalacion

```bash
python3 -m venv fac
./fac/bin/pip install -r requirements.txt
cp .env.example .env      # y edita los valores
```

### Con SQLite (rapido, para probar)

En `.env` pon `USAR_SQLITE=True`. No hace falta tener MySQL instalado.

### Con MySQL

```sql
CREATE DATABASE facturas CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'facturacion'@'localhost' IDENTIFIED BY 'tu-clave';
GRANT ALL PRIVILEGES ON facturas.* TO 'facturacion'@'localhost';
FLUSH PRIVILEGES;
```

## Puesta en marcha

```bash
./fac/bin/python manage.py migrate
./fac/bin/python manage.py seed_demo     # datos de ejemplo
./fac/bin/python manage.py runserver
```

`seed_demo` crea la configuracion del negocio, seis facturas en el ano con
una anulada, una factura de 12 productos que cabe en una sola hoja y otra de
40 productos que ocupa varias paginas. Usa `--borrar` para reiniciar los datos,
la configuracion y los consecutivos del ano (FAC y OC).

## Pruebas

```bash
USAR_SQLITE=1 ./fac/bin/python -m pytest
```

Las pruebas del PDF no se limitan a comprobar que el archivo exista: leen el
PDF generado, descifran el contenido, y revisan que el texto no se salga de los
margenes ni se monte sobre otro bloque. Cambios de contenido, de diseno o de
tipografia en el PDF se ven en los resultados.

Estado actual: **199 pruebas, todas en verde (mas 2 subtests).**

| Archivo | Que cubre |
| --- | --- |
| `facturacion/tests/test_totales.py` | calculos internos de lineas, ITBMS y totales |
| `facturacion/tests/test_serie.py` | consecutivo anual, codigo de verificacion, duplicados y anulaciones |
| `facturacion/tests/test_numero_a_letras.py` | montos en letras, hasta millones |
| `facturacion/tests/test_pdf.py` | estructura del PDF, colores, notas, firmas, margenes, solapes y factura de 40 productos |
| `facturacion/tests/test_vistas.py` | pantallas, creacion, notas, formulario sin descuentos, duplicado, verificacion y configuracion |
| `facturacion/tests/utiles_pdf.py` | utilerias para inspeccionar el PDF en las pruebas |

## Pantallas

| Ruta | Que hace |
| --- | --- |
| `/` | crear una factura |
| `/historial/` | listado con busqueda y paginacion |
| `/factura/<id>/` | detalle de una factura |
| `/factura/<id>/pdf/` | descarga el PDF |
| `/factura/<id>/duplicar/` | abre el formulario con los datos copiados |
| `/factura/<id>/anular/` | anula la factura (marca de agua en el PDF) |
| `/verificar/<serie>/<codigo>/` | consulta publica de una factura |
| `/configuracion/` | datos del negocio, tres colores, notas por defecto y logo |

## Reglas de negocio

**Numeracion.** Cada ano tiene su propio consecutivo con el formato
`FAC-AAAA-0001`. El numero se reserva dentro de una transaccion con
`select_for_update()`, asi que dos usuarios simultaneos nunca reciben el
mismo numero.

**Orden de compra.** Puedes escribir la orden de compra a mano en el
formulario. Si la dejas vacia, se asigna una automatica con el formato
`OC-AAAA-0001`, con su propio consecutivo por ano e independiente de la serie
FAC. Una OC manuscrita no altera el consecutivo. Ni la serie ni la OC
reutilizan numeros: anular una factura no libera el numero que llevo.

**RUC opcional.** La factura puede mostrar o no el RUC del cliente
(marcador en el formulario) y la configuracion del negocio decide si se
imprime el RUC de la empresa. Ocultarlo deja el dato fuera del PDF sin dejar
huecos.

**Precio por caja o por unidad.** El precio se guarda por la caja completa y
cada linea decide como se cobra: por **caja** (el precio entero, la cantidad
se lee como cajas) o por **unidad** (el precio de la caja se divide entre las
unidades que trae). El formulario muestra "Caja de N und" y un selector
"Cobrar por" en cada linea; el PDF imprime la misma referencia ("Caja de
24 und"), la cantidad con su unidad ("12.00 und", "2.00 cajas") y el precio
efectivo ("0.50 / und", "30.00 / caja").

**Calculos.** Todos los montos usan `Decimal` y se redondean con
`ROUND_HALF_UP` a dos decimales. El monto de cada linea es
`cantidad x precio efectivo` (la caja o la unidad); el ITBMS (7%) se aplica
solo a las lineas marcadas como gravadas. El gran total siempre es
`subtotal + ITBMS`, porque la factura no ofrece ni descuentos ni portes.

**Codigo de verificacion.** Es un HMAC-SHA256 de 12 caracteres derivado del
numero de serie, la fecha y el total. No se guarda en la base: se recalcula al
verificar, de modo que un codigo no se puede alterar sin que deje de coincidir.
El QR lleva el texto del codigo, sin enlace, para que se pueda leer sin
conexion a internet. Bajo el QR va la serie de la factura.

**Anulacion.** No borra la factura: la marca como anulada y guarda la fecha.
El PDF correspondiente lleva la marca de agua `ANULADA`.

**PDF.** Carta vertical, margenes de 15 mm, Helvetica y tamano minimo de 8 pt.
Junto a la serie se imprime la fecha de creacion y el vencimiento: un anio
calendario despues, calculado automaticamente. La tabla de productos se repite
en cada pagina con su encabezado
"Precio unit." y el bloque que cierra la factura (subtotal, ITBMS, gran total,
total en letras, notas y firmas) queda siempre entero en la ultima pagina.
El PDF muestra la cantidad con su unidad ("12.00 und", "2.00 cajas"), el
precio efectivo ("1.25 / und", "30.00 / caja") y, cuando la linea tiene caja,
la referencia "Caja de N und" junto al producto. Las tres filas de totales se
presentan solas, sin columnas de descuento ni portes. Una factura de 12
productos de descripcion corta cabe en una sola hoja; las descripciones largas
se ajustan en varias lineas.

## Configuracion

Todo se ajusta desde la pantalla `/configuracion/` o por variables de entorno
en `.env`:

| Variable | Para que sirve |
| --- | --- |
| `SECRET_KEY` | clave de Django; cambiala en produccion |
| `DEBUG` | `False` en produccion |
| `ALLOWED_HOSTS` | dominios permitidos, separados por comas |
| `CSRF_TRUSTED_ORIGINS` | origenes confiables, separados por comas |
| `USAR_SQLITE` | `True` para usar el archivo local en vez de MySQL |
| `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` | conexion a MySQL |

Los datos del negocio (nombre, RUC, direccion, logo, datos bancarios y el
texto de notas por defecto, que la factura nueva trae ya escrito) se editan en
la pantalla de configuracion. Tambien hay tres selectores de color: el color de
la marca, el de la barra ORDEN DE COMPRA y el de la tabla y los totales. Se aplican de
inmediato a los PDF.

## Ejemplo

En `docs/ejemplo_factura.pdf` hay una factura de una hoja (12 productos) y en
`docs/ejemplo_factura_40_items.pdf` una de 40 productos en varias paginas.
Ambas se generan con `seed_demo` y suelen refrescarse con:

```bash
USAR_SQLITE=1 ./fac/bin/python manage.py seed_demo --borrar
```

y volviendo a generar los dos PDF desde la aplicacion.
