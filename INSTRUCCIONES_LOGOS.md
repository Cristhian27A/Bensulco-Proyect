# Instrucciones para Agregar Logos Corporativos

## Encabezado Rediseñado

El encabezado del catálogo ha sido rediseñado con un diseño profesional y corporativo.

## Cambios Realizados:

### 1. Fondo Morado Sólido
- **Antes**: Degradado morado (`#6B21A8` → `#9333EA` → `#A855F7`)
- **Ahora**: Color morado sólido y profundo (`#581c87`)
- **Resultado**: Más elegante, corporativo y consistente con la identidad de marca

### 2. Layout Flexbox Profesional
- **Izquierda**: Logo de Bensulco Distribution
- **Centro**: Título "Catálogo de Productos" + Subtítulo "Bensulco Distribution & Blixi"
- **Derecha**: Logo de Blixi + Navegación (Catálogo + Carrito)

### 3. Eliminación de Redundancias
- **Antes**: "Catálogo de Productos", "Blixi", "Catálogo" (repetitivo)
- **Ahora**: "Catálogo de Productos" + "Bensulco Distribution & Blixi" (limpio y profesional)

### 4. Archivos Estáticos
- Carpeta creada: `catalogo/static/catalogo/images/`
- Configuración actualizada en `settings.py` para incluir esta carpeta
- README incluido con instrucciones

## Cómo Agregar los Logos:

### Opción 1: Colocar los archivos directamente
1. Coloque `bensulco-logo.png` en `catalogo/static/catalogo/images/`
2. Coloque `blixi-logo.png` en `catalogo/static/catalogo/images/`
3. Los logos aparecerán automáticamente en el encabezado

### Opción 2: Requisitos de los logos
- **Formato**: PNG con transparencia recomendado
- **Altura**: 50px (se ajusta automáticamente)
- **Nombre exacto**: 
  - `bensulco-logo.png` para Bensulco Distribution
  - `blixi-logo.png` para Blixi
- **Calidad**: Alta resolución para mantener nitidez

### Opción 3: Comportamiento sin logos
- Si un logo no está disponible, el espacio se colapsa automáticamente
- El diseño sigue funcionando perfectamente sin logos
- Se usa el atributo `onerror="this.style.display='none'"` para manejar esto

## Diseño Responsivo:

### Desktop (> 1024px)
- Layout horizontal completo
- Logos a izquierda y derecha
- Título centrado
- Navegación visible

### Tablet (768px - 1024px)
- Layout horizontal pero más compacto
- Títulos ligeramente más pequeños
- Espaciado reducido

### Móvil (< 768px)
- Layout vertical
- Título arriba
- Logos centrados
- Navegación abajo
- Tamaño de logos reducido a 40px

## Características del Nuevo Header:

1. **Color Sólido Corporativo**: `#581c87` (morado profundo)
2. **Sombra Elegante**: Box-shadow con opacidad 0.4
3. **Tipografía Limpia**: Font-weight 700 para títulos
4. **Navegación Estilizada**: Links con hover effect
5. **Badge de Carrito**: Distinguido con fondo semitransparente
6. **Responsive**: Adaptable a todos los dispositivos

## Archivos Modificados:

1. `catalogo/templates/catalogo/base.html` - Rediseño completo del header
2. `catalogo/static/catalogo/images/` - Nueva carpeta para logos
3. `catalogo/static/catalogo/images/README.md` - Instrucciones para logos
4. `facturas/settings.py` - Agregado `catalogo/static` a STATICFILES_DIRS

## Verificación:

El sistema funciona correctamente sin logos (los espacios se colapsan). Cuando agregue los logos, aparecerán automáticamente en el encabezado.
