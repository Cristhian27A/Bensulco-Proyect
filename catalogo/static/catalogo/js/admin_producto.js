(function($) {
    'use strict';

    $(document).ready(function() {
        // Ocultar campo de precio_media_caja si permite_media_caja está desmarcado
        function togglePrecioMediaCaja() {
            var permiteMediaCaja = $('#id_permite_media_caja').is(':checked');
            var precioMediaCajaField = $('#id_precio_media_caja').closest('.form-row');

            if (permiteMediaCaja) {
                precioMediaCajaField.show();
            } else {
                precioMediaCajaField.hide();
            }
        }

        // Adaptar formulario cuando se selecciona la categoría "Media caja"
        function toggleCategoriaMediaCaja() {
            var categoria = $('#id_categoria').val();
            var esMediaCaja = categoria && categoria.toLowerCase().includes('media caja');
            
            console.log('Categoría seleccionada:', categoria, '¿Es Media caja?', esMediaCaja);
            
            // Campos de precios
            var precioCajaField = $('#id_precio_caja').closest('.form-row');
            var precioMediaCajaField = $('#id_precio_media_caja').closest('.form-row');
            var precioUnidadField = $('#id_precio_unidad').closest('.form-row');
            var precioConsumidorField = $('#id_precio_consumidor').closest('.form-row');
            var unidadesCajaField = $('#id_unidades_por_caja').closest('.form-row');
            var permiteMediaCajaField = $('#id_permite_media_caja').closest('.form-row');
            
            if (esMediaCaja) {
                // Para productos de media caja, ocultar precio_caja y permite_media_caja
                // Mostrar solo campos relevantes: precio_media_caja, precio_unidad, precio_consumidor, unidades_por_caja
                if (precioCajaField) precioCajaField.hide();
                if (permiteMediaCajaField) permiteMediaCajaField.hide();
                
                // Mostrar campos de media caja
                if (precioMediaCajaField) precioMediaCajaField.show();
                if (precioUnidadField) precioUnidadField.show();
                if (precioConsumidorField) precioConsumidorField.show();
                if (unidadesCajaField) unidadesCajaField.show();
                
                // Cambiar label de unidades_por_caja para que sea más claro
                if (unidadesCajaField) {
                    var label = unidadesCajaField.find('label');
                    if (label.length > 0) {
                        label.text('Unidades por media caja:');
                    }
                }
                
                // Marcar permite_media_caja como true automáticamente
                $('#id_permite_media_caja').prop('checked', true);
                
                console.log('Modo Media caja activado');
            } else {
                // Para productos normales, comportamiento estándar
                if (precioCajaField) precioCajaField.show();
                if (permiteMediaCajaField) permiteMediaCajaField.show();
                
                // Aplicar lógica estándar de permite_media_caja
                togglePrecioMediaCaja();
                
                // Restaurar label original
                if (unidadesCajaField) {
                    var label = unidadesCajaField.find('label');
                    if (label.length > 0) {
                        label.text('Unidades por caja:');
                    }
                }
                
                console.log('Modo producto normal activado');
            }
        }

        // Ejecutar al cargar
        togglePrecioMediaCaja();
        toggleCategoriaMediaCaja();

        // Ejecutar cuando cambia el checkbox permite_media_caja
        $('#id_permite_media_caja').on('change', togglePrecioMediaCaja);
        
        // Ejecutar cuando cambia la categoría
        $('#id_categoria').on('change', toggleCategoriaMediaCaja);
    });
})(django.jQuery);
