/* Formulario de factura: filas dinámicas y totales en vivo.
 *
 * El cálculo de aquí es una copia exacta de facturacion/services/totales.py.
 * Se trabaja en CENTAVOS (enteros) para no arrastrar errores de coma
 * flotante, igual que el Decimal del servidor.
 *
 *   monto    = cantidad x precio (de caja o unidad), redondeado UNA vez.
 *   subtotal = redondeo de la suma de los brutos (sin redondear por línea)
 *   ITBMS    = redondeo(suma de los montos gravados x 0.07)
 *   total    = subtotal + ITBMS
 *
 * No hay descuentos ni portes. Cada línea cobra por UNIDAD (precio de la
 * caja dividido entre las unidades que trae) o por CAJA (precio entero).
 * El servidor vuelve a calcular todo al guardar; esta vista es la
 * referencia en pantalla.
 */

(function () {
    "use strict";

    var cuerpo = document.getElementById("cuerpo-productos");
    if (!cuerpo) { return; }

    var botonAgregar = document.getElementById("agregar-fila");
    var plantilla = document.getElementById("plantilla-fila");
    var totalFormulario = document.querySelector("#id_linea-TOTAL_FORMS");
    var avisoSinFilas = document.getElementById("aviso-sin-filas");
    var casillaItbms = document.getElementById("id_aplicar_itbms");
    var casillaTotales = document.getElementById("js-ver-totales");
    var cuadroTotales = document.getElementById("cuadro-totales");

    var PREFIJO = "linea";
    var POR_CAJA = "caja";

    /* ---------- aritmética en centavos ---------- */

    // Convierte lo que escribe el usuario a centavos enteros.
    // Redondea a 2 decimales, igual que quantize(Decimal, 0.01).
    function centavos(valor) {
        var numero = parseFloat(valor);
        if (isNaN(numero)) { return 0; }
        return Math.round(numero * 100);
    }

    function unidadesDeCaja(valor) {
        var unidades = parseInt(valor, 10);
        if (isNaN(unidades) || unidades < 1) { return 1; }
        return unidades;
    }

    function texto(valor) {
        return valor.toFixed(2);
    }

    // Precio por el que se multiplica la cantidad: la caja entera o la
    // unidad suelta (precio de la caja / unidades que trae). Sin redondear.
    function precioEfectivo(precio, unidades, modo) {
        if (modo === POR_CAJA || unidades <= 1) { return precio; }
        return precio / unidades;
    }

    // Convierte el precio efectivo a un texto corto, igual que la función
    // formato_precio del servidor: hasta 4 decimales, sin ceros de más.
    function textoPrecio(precio) {
        var texto4 = precio.toFixed(4);
        if (precio % 1 === 0) { return texto4.split(".")[0] + ".00"; }
        var sinCeros = texto4.replace(/0+$/, "").replace(/\.$/, "");
        if (sinCeros.indexOf(".") >= 0) {
            var partes = sinCeros.split(".");
            if (partes[1].length === 1) { sinCeros += "0"; }
        } else {
            sinCeros += ".00";
        }
        return sinCeros;
    }

    // Monto de la línea, en centavos, redondeado una sola vez al final.
    // En caja:  round(cantidad x precio).  En unidad: round(cantidad x
    // precio_caja / unidades) -> el precio unitario puede ser inexacto y
    // redondea igual que el servidor (0.005 hacia arriba).
    function montoLinea(cantidad, precioCaja, unidades, modo) {
        var cant = centavos(cantidad);
        var prec = centavos(precioCaja);
        if (cant <= 0 || prec < 0) { return 0; }
        if (modo === POR_CAJA) {
            return Math.round((cant * prec) / 100);
        }
        return Math.round((cant * prec) / (100 * unidadesDeCaja(unidades)));
    }

    function calcular() {
        var filas = cuerpo.querySelectorAll(".fila-producto");
        var subtotalBruto = 0;
        var baseGravada = 0;
        var conDatos = 0;
        var itbmsGlobal = casillaItbms ? casillaItbms.checked : true;

        Array.prototype.forEach.call(filas, function (fila) {
            var cantidad = fila.querySelector(".js-cantidad");
            var precio = fila.querySelector(".js-precio");
            var unidades = fila.querySelector(".js-upxc");
            var modo = fila.querySelector(".js-cobrar-por");
            var gravada = fila.querySelector(".js-gravada");
            var casillaMonto = fila.querySelector(".js-monto");
            var casillaPrecioEfectivo = fila.querySelector(".js-precio-efectivo");
            var casillaPrecioParaMostrar = fila.querySelector(".js-precio-para-mostrar");

            var cantValor = cantidad ? cantidad.value : "";
            var precValor = precio ? precio.value : "";
            var unidadesValor = unidades ? unidades.value : "1";
            var modoValor = modo ? modo.value : "";
            var unidadesN = unidadesDeCaja(unidadesValor);

            var monto = montoLinea(cantValor, precValor, unidadesValor, modoValor);
            var precioCaja = centavos(precValor) / 100;
            var precioEf = precioEfectivo(precioCaja, unidadesN, modoValor);
            var sufijo = modoValor === POR_CAJA ? " / caja" : " / und";

            if (casillaMonto) {
                casillaMonto.textContent = texto(monto / 100);
            }

            // Precio de la unidad suelta (o de la caja) que muestra la fila.
            if (casillaPrecioEfectivo) {
                casillaPrecioEfectivo.textContent =
                    (precioCaja > 0 ? textoPrecio(precioEf) + sufijo : "0.00 / und");
            }
            if (casillaPrecioParaMostrar) {
                casillaPrecioParaMostrar.textContent =
                    precioCaja > 0 ? "Precio: " + textoPrecio(precioEf) + sufijo : "";
            }

            if (centavos(cantValor) > 0 && centavos(precValor) > 0) {
                conDatos += 1;
            }

            // El bruto se acumula sin redondear; el subtotal se redondea
            // una sola vez al final, como hace el servidor.
            subtotalBruto += (centavos(cantValor) * centavos(precValor))
                / (modoValor === POR_CAJA ? 100 : 100 * unidadesN);

            // Con el ITBMS global activado, todas las lineas son gravadas.
            var esGravada = itbmsGlobal ? true : (gravada ? gravada.checked : true);
            if (esGravada) {
                baseGravada += monto;
            }

            if (gravada) {
                gravada.disabled = itbmsGlobal;
            }
        });

        var subtotal = Math.round(subtotalBruto);
        var baseGravadaCentavos = Math.round(baseGravada);
        var itbms = itbmsGlobal ? Math.round((baseGravadaCentavos * 7) / 100) : 0;
        var total = subtotal + itbms;

        escribir("t-subtotal", subtotal);
        escribir("t-itbms", itbms);
        escribir("t-total", total);

        if (avisoSinFilas) {
            avisoSinFilas.textContent = conDatos > 0
                ? conDatos + (conDatos === 1 ? " producto listo." : " productos listos.")
                : "Agrega al menos un producto con cantidad y precio.";
        }

        renumerar();
    }

    function escribir(id, centavosValor) {
        var nodo = document.getElementById(id);
        if (nodo) {
            nodo.textContent = texto(centavosValor / 100);
        }
    }

    function renumerar() {
        var filas = cuerpo.querySelectorAll(".fila-producto");
        Array.prototype.forEach.call(filas, function (fila, indice) {
            var numero = fila.querySelector(".col-numero");
            if (numero) { numero.textContent = indice + 1; }
        });
    }

    /* ---------- filas dinámicas ---------- */

    function agregarFila() {
        var indice = parseInt(totalFormulario.value, 10) || 0;
        var html = plantilla.innerHTML.split("__PREFIX__").join(PREFIJO + "-" + indice);
        var envoltorio = document.createElement("tbody");
        envoltorio.innerHTML = html.trim();
        var fila = envoltorio.firstElementChild;
        cuerpo.appendChild(fila);
        totalFormulario.value = indice + 1;

        var quitar = fila.querySelector(".js-quitar");
        if (quitar) { quitar.addEventListener("click", quitarFila); }

        var descripcion = fila.querySelector(".campo-producto");
        if (descripcion) { descripcion.focus(); }
        calcular();
        return fila;
    }

    function quitarFila(evento) {
        var fila = evento.currentTarget.closest(".fila-producto");
        if (fila) { fila.remove(); }
        calcular();
    }

    /* ---------- arranque ---------- */

    Array.prototype.forEach.call(
        cuerpo.querySelectorAll(".fila-producto .js-quitar"),
        function (boton) { boton.addEventListener("click", quitarFila); }
    );

    if (botonAgregar) {
        botonAgregar.addEventListener("click", agregarFila);
    }

    cuerpo.addEventListener("input", calcular);
    cuerpo.addEventListener("change", calcular);

    [casillaItbms].forEach(function (campo) {
        if (campo) {
            campo.addEventListener("input", calcular);
            campo.addEventListener("change", calcular);
        }
    });

    if (casillaTotales && cuadroTotales) {
        casillaTotales.addEventListener("change", function () {
            cuadroTotales.classList.toggle("oculto", !casillaTotales.checked);
        });
    }

    calcular();
})();
