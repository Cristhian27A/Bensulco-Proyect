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

    console.log("Autocompletado: Script formulario.js cargado");

    var cuerpo = document.getElementById("cuerpo-productos");
    if (!cuerpo) { 
        console.log("Autocompletado: No se encontró cuerpo-productos, saliendo");
        return; 
    }
    
    console.log("Autocompletado: cuerpo-productos encontrado");

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

    // Precio por el que se multiplica la cantidad:
    // - "caja": usa precio_caja completo
    // - "unidad": usa precio_unitario directamente (para tiendas pequeñas)
    // Sin redondear.
    function precioEfectivo(precio, unidades, modo, precioUnidad) {
        if (modo === POR_CAJA) { return precio; }
        // Para unidad: usa precio_unidad si existe, si no usa precio_caja
        if (precioUnidad && precioUnidad > 0) { return precioUnidad; }
        return precio;  // precio_caja es en realidad el precio por unidad en este caso
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
    // En caja:  round(cantidad x precio_caja)
    // En unidad: round(cantidad x precio_unitario)
    // Redondea igual que el servidor (0.005 hacia arriba).
    function montoLinea(cantidad, precioCaja, unidades, modo, precioUnidad) {
        var cant = centavos(cantidad);
        var prec = centavos(precioCaja);
        if (cant <= 0 || prec < 0) { return 0; }
        if (modo === POR_CAJA) {
            return Math.round((cant * prec) / 100);
        }
        // Para unidad: usa precio_unitario si existe, si no usa precio_caja
        var precioUsar = (precioUnidad && precioUnidad > 0) ? centavos(precioUnidad) : prec;
        return Math.round((cant * precioUsar) / 100);
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
            var precioUnidad = fila.querySelector(".js-precio-unidad");
            var unidades = fila.querySelector(".js-upxc");
            var modo = fila.querySelector(".js-cobrar-por");
            var gravada = fila.querySelector(".js-gravada");
            var casillaMonto = fila.querySelector(".js-monto");
            var casillaPrecioEfectivo = fila.querySelector(".js-precio-efectivo");
            var casillaPrecioParaMostrar = fila.querySelector(".js-precio-para-mostrar");

            var cantValor = cantidad ? cantidad.value : "";
            var precValor = precio ? precio.value : "";
            var precUnidadValor = precioUnidad ? precioUnidad.value : "";
            var unidadesValor = unidades ? unidades.value : "1";
            var modoValor = modo ? modo.value : "";
            var unidadesN = unidadesDeCaja(unidadesValor);

            var monto = montoLinea(cantValor, precValor, unidadesValor, modoValor, precUnidadValor);
            var precioCaja = centavos(precValor) / 100;
            var precioUnid = centavos(precUnidadValor) / 100;
            var precioEf = precioEfectivo(precioCaja, unidadesN, modoValor, precioUnid);
            var sufijo = modoValor === POR_CAJA ? " / caja" : " / und";

            if (casillaMonto) {
                casillaMonto.textContent = texto(monto / 100);
            }

            // Precio de la unidad suelta (o de la caja) que muestra la fila.
            if (casillaPrecioEfectivo) {
                casillaPrecioEfectivo.textContent =
                    (precioCaja > 0 || precioUnid > 0 ? textoPrecio(precioEf) + sufijo : "0.00 / und");
            }
            if (casillaPrecioParaMostrar) {
                casillaPrecioParaMostrar.textContent =
                    (precioCaja > 0 || precioUnid > 0 ? "Precio: " + textoPrecio(precioEf) + sufijo : "");
            }

            if (centavos(cantValor) > 0 && (centavos(precValor) > 0 || centavos(precUnidadValor) > 0)) {
                conDatos += 1;
            }

            // El bruto se acumula sin redondear; el subtotal se redondea
            // una sola vez al final, como hace el servidor.
            if (modoValor === POR_CAJA) {
                subtotalBruto += (centavos(cantValor) * centavos(precValor)) / 100;
            } else {
                // Para unidad: usa precio_unidad si existe, si no usa precio_caja
                var precioUsar = (precUnidadValor && precUnidadValor > 0) ? centavos(precUnidadValor) : centavos(precValor);
                subtotalBruto += (centavos(cantValor) * precioUsar) / 100;
            }

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

    /* ---------- autocompletado de productos ---------- */

    var timeoutBusqueda = null;
    var menuSugerencias = null;

    function crearMenuSugerencias() {
        if (menuSugerencias) return menuSugerencias;
        
        menuSugerencias = document.createElement("div");
        menuSugerencias.className = "menu-sugerencias";
        menuSugerencias.style.display = "none";
        menuSugerencias.style.position = "absolute";
        menuSugerencias.style.zIndex = "9999";
        menuSugerencias.style.background = "white";
        menuSugerencias.style.border = "1px solid #ddd";
        menuSugerencias.style.borderRadius = "4px";
        menuSugerencias.style.boxShadow = "0 4px 12px rgba(0,0,0,0.15)";
        menuSugerencias.style.maxWidth = "400px";
        menuSugerencias.style.maxHeight = "300px";
        menuSugerencias.style.overflowY = "auto";
        document.body.appendChild(menuSugerencias);
        
        // Cerrar al hacer clic fuera
        document.addEventListener("click", function(evento) {
            if (!menuSugerencias.contains(evento.target)) {
                menuSugerencias.style.display = "none";
            }
        });
        
        return menuSugerencias;
    }

    function buscarProductos(query, callback) {
        console.log('Autocompletado: Buscando productos con query:', query);
        
        if (timeoutBusqueda) {
            clearTimeout(timeoutBusqueda);
        }
        
        if (query.length < 2) {
            console.log('Autocompletado: Query muy corto, ocultando menú');
            callback([]);
            if (menuSugerencias) {
                menuSugerencias.style.display = "none";
            }
            return;
        }
        
        console.log('Autocompletado: Haciendo fetch a /catalogo/api/buscar-productos/?q=' + query);
        timeoutBusqueda = setTimeout(function() {
            fetch("/catalogo/api/buscar-productos/?q=" + encodeURIComponent(query))
                .then(function(response) {
                    console.log('Autocompletado: Response recibida:', response.status);
                    return response.json();
                })
                .then(function(data) {
                    console.log('Autocompletado: Data recibida:', data);
                    callback(data.results);
                })
                .catch(function(error) {
                    console.error("Error al buscar productos:", error);
                    callback([]);
                });
        }, 300);
    }

    function mostrarSugerencias(productos, input) {
        console.log('Autocompletado: Mostrando', productos.length, 'sugerencias para input:', input);
        var menu = crearMenuSugerencias();
        menu.innerHTML = "";
        
        if (productos.length === 0) {
            console.log('Autocompletado: No hay resultados, ocultando menú');
            menu.style.display = "none";
            return;
        }
        
        console.log('Autocompletado: Creando items de sugerencias');
        productos.forEach(function(producto) {
            var item = document.createElement("div");
            item.className = "sugerencia-item";
            item.style.padding = "10px 15px";
            item.style.cursor = "pointer";
            item.style.borderBottom = "1px solid #f0f0f0";
            item.style.transition = "background 0.2s";
            
            item.innerHTML = "<strong>" + producto.nombre + "</strong><br>" +
                           "<small>SKU: " + producto.sku + 
                           (producto.codigo_barras ? " | Código: " + producto.codigo_barras : "") +
                           " | $" + producto.precio_caja + " (caja) | $" + producto.precio_unidad + " (und)" +
                           "</small>";
            
            item.addEventListener("mouseenter", function() {
                item.style.background = "#f8f9fa";
            });
            
            item.addEventListener("mouseleave", function() {
                item.style.background = "white";
            });
            
            item.addEventListener("click", function() {
                console.log('Autocompletado: Producto seleccionado:', producto.nombre);
                seleccionarProducto(producto, input);
                menu.style.display = "none";
            });
            
            menu.appendChild(item);
        });
        
        // Posicionar el menú cerca del input
        var rect = input.getBoundingClientRect();
        console.log('Autocompletado: Posición input - top:', rect.bottom, 'left:', rect.left, 'width:', rect.width);
        menu.style.top = (rect.bottom + window.scrollY + 2) + "px";
        menu.style.left = rect.left + "px";
        menu.style.width = Math.max(rect.width, 400) + "px";
        menu.style.display = "block";
        console.log('Autocompletado: Menú mostrado');
    }

    function seleccionarProducto(producto, input) {
        console.log('Autocompletado: seleccionarProducto llamado con producto:', producto.nombre);
        var fila = input.closest(".fila-producto");
        console.log('Autocompletado: Fila encontrada:', !!fila);
        
        if (!fila) {
            console.error('Autocompletado: No se encontró la fila del producto');
            return;
        }
        
        // Llenar nombre/descripción
        var descripcion = fila.querySelector(".campo-producto");
        console.log('Autocompletado: Campo descripcion encontrado:', !!descripcion);
        if (descripcion) {
            descripcion.value = producto.nombre;
            console.log('Autocompletado: Descripción llenada:', producto.nombre);
        }
        
        // Llenar código de barras
        var codigoBarras = fila.querySelector(".campo-codigo-barras");
        console.log('Autocompletado: Campo codigo_barras encontrado:', !!codigoBarras);
        if (codigoBarras) {
            codigoBarras.value = producto.codigo_barras;
            console.log('Autocompletado: Código de barras llenado:', producto.codigo_barras);
        }
        
        // Llenar unidades por caja
        var unidadesCaja = fila.querySelector(".campo-unidades-caja");
        if (!unidadesCaja) {
            // Fallback: buscar input con name que contiene unidades_por_caja
            var inputs = fila.querySelectorAll("input[type='number']");
            inputs.forEach(function(inp) {
                if (inp.name && inp.name.includes("unidades_por_caja")) {
                    unidadesCaja = inp;
                }
            });
        }
        console.log('Autocompletado: Campo unidades_caja encontrado:', !!unidadesCaja);
        if (unidadesCaja) {
            unidadesCaja.value = producto.unidades_por_caja;
            console.log('Autocompletado: Unidades por caja llenadas:', producto.unidades_por_caja);
        }
        
        // Llenar precio caja
        var precioCaja = fila.querySelector(".campo-precio-caja");
        if (!precioCaja) {
            // Fallback: buscar input con name que contiene precio_unitario
            var inputs = fila.querySelectorAll("input[type='number']");
            inputs.forEach(function(inp) {
                if (inp.name && inp.name.includes("precio_unitario")) {
                    precioCaja = inp;
                }
            });
        }
        console.log('Autocompletado: Campo precio_caja encontrado:', !!precioCaja);
        if (precioCaja) {
            precioCaja.value = producto.precio_caja;
            console.log('Autocompletado: Precio caja llenado:', producto.precio_caja);
        }
        
        // Llenar precio unidad
        var precioUnidad = fila.querySelector(".campo-precio-unidad");
        if (!precioUnidad) {
            // Fallback: buscar input con name que contiene precio_unidad
            var inputs = fila.querySelectorAll("input[type='number']");
            inputs.forEach(function(inp) {
                if (inp.name && inp.name.includes("precio_unidad")) {
                    precioUnidad = inp;
                }
            });
        }
        console.log('Autocompletado: Campo precio_unidad encontrado:', !!precioUnidad);
        if (precioUnidad) {
            precioUnidad.value = producto.precio_unidad;
            console.log('Autocompletado: Precio unidad llenado:', producto.precio_unidad);
        }
        
        // Recalcular totales
        console.log('Autocompletado: Recalculando totales');
        calcular();
    }

    function configurarAutocompletado(fila) {
        console.log('Autocompletado: Configurando fila', fila);
        
        var descripcion = fila.querySelector(".campo-producto");
        var codigoBarras = fila.querySelector(".campo-codigo-barras");
        
        console.log('Autocompletado: Campo producto encontrado:', !!descripcion);
        console.log('Autocompletado: Campo codigo_barras encontrado:', !!codigoBarras);
        
        if (descripcion) {
            descripcion.addEventListener("input", function() {
                var query = this.value.trim();
                console.log('Autocompletado: Input en producto, query:', query);
                buscarProductos(query, function(productos) {
                    mostrarSugerencias(productos, descripcion);
                });
            });
        }
        
        if (codigoBarras) {
            codigoBarras.addEventListener("input", function() {
                var query = this.value.trim();
                console.log('Autocompletado: Input en código_barras, query:', query);
                buscarProductos(query, function(productos) {
                    mostrarSugerencias(productos, codigoBarras);
                });
            });
        }
    }

    function agregarFila() {
        var indice = parseInt(totalFormulario.value, 10) || 0;
        var html = plantilla.innerHTML.split("__PREFIX__").join(PREFIJO + "-" + indice);
        // Usar insertAdjacentHTML para mejor preservación de elementos
        cuerpo.insertAdjacentHTML("beforeend", html.trim());
        var fila = cuerpo.lastElementChild;
        totalFormulario.value = indice + 1;

        var quitar = fila.querySelector(".js-quitar");
        if (quitar) { quitar.addEventListener("click", quitarFila); }

        // Asegurar que el select de "Cobrar por" funcione correctamente
        var cobrarPor = fila.querySelector(".js-cobrar-por");
        if (cobrarPor) {
            // Asegurar que las opciones estén presentes
            if (cobrarPor.options.length === 0) {
                // Si por alguna razón no hay opciones, agregarlas manualmente
                var optUnidad = document.createElement("option");
                optUnidad.value = "unidad";
                optUnidad.text = "Unidad";
                optUnidad.selected = true;
                cobrarPor.add(optUnidad);

                var optCaja = document.createElement("option");
                optCaja.value = "caja";
                optCaja.text = "Caja";
                cobrarPor.add(optCaja);
            } else {
                // Establecer valor por defecto
                cobrarPor.value = "unidad";
            }
            // Forzar que el select sea interactivo
            cobrarPor.disabled = false;
            cobrarPor.style.pointerEvents = "auto";
        }

        // Configurar autocompletado en la nueva fila
        configurarAutocompletado(fila);

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

    // Configurar autocompletado en filas existentes
    Array.prototype.forEach.call(
        cuerpo.querySelectorAll(".fila-producto"),
        function (fila) { configurarAutocompletado(fila); }
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
