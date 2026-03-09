# NovaGravity Design System - Documentación

## Tabla de Contenidos

1. [Introducción](#introducción)
2. [Paleta de Colores](#paleta-de-colores)
3. [Tipografía](#tipografía)
4. [Efectos Glassmorphism](#efectos-glassmorphism)
5. [Componentes Reutilizables](#componentes-reutilizables)
6. [Sistema de Animaciones](#sistema-de-animaciones)
7. [Guía de Implementación](#guía-de-implementación)
8. [Mejores Prácticas](#mejores-prácticas)

## Introducción

El sistema de diseño de NovaGravity está construido para crear interfaces modernas, profesionales y coherentes con efectos avanzados de glassmorphism, animaciones fluidas y una paleta de colores optimizada para la productividad y el engagement.

### Principios de Diseño

- **Consistencia**: Componentes reutilizables con estilos uniformes
- **Accesibilidad**: Contraste adecuado y tipografía legible
- **Rendimiento**: Animaciones optimizadas y efectos CSS eficientes
- **Flexibilidad**: Adaptable a diferentes contextos y necesidades
- **Innovación**: Uso de técnicas modernas como glassmorphism y parallax

## Paleta de Colores

### Colores Primarios

```css
--primary-500: #8b5cf6  /* Morado principal - Innovación */
--primary-600: #7c3aed  /* Morado oscuro - Profundidad */
--primary-400: #a78bfa  /* Morado claro - Creatividad */
```

### Colores Secundarios

```css
--secondary-400: #38bdf8  /* Azul cielo - Confianza */
--secondary-500: #0ea5e9  /* Azul principal - Estabilidad */
```

### Colores de Acento

```css
--accent-400: #f87171    /* Rosa vibrante - Energía */
--accent-500: #ef4444    /* Rosa principal - Acción */
```

### Colores Semánticos

```css
--success-500: #22c55e  /* Verde - Éxito */
--warning-500: #f59e0b  /* Naranja - Advertencia */
--danger-500: #ef4444    /* Rojo - Error */
--info-500: #3b82f6     /* Azul - Información */
```

### Colores Neutros

```css
--dark-900: #111827    /* Texto oscuro principal */
--dark-800: #1f2937    /* Texto oscuro secundario */
--dark-500: #6b7280    /* Texto gris */
--light-100: #f3f4f6   /* Fondo claro */
--light-50: #f9fafb    /* Fondo más claro */
```

### Efectos Glassmorphism

```css
--glass-bg-1: rgba(255, 255, 255, 0.05)  /* Fondo glass suave */
--glass-bg-2: rgba(255, 255, 255, 0.1)   /* Fondo glass medio */
--glass-bg-3: rgba(255, 255, 255, 0.15)  /* Fondo glass fuerte */
--glass-border: rgba(255, 255, 255, 0.1) /* Borde glass */
--glass-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.08) /* Sombra glass */
```

## Tipografía

### Fuentes Principales

```css
--font-primary: 'Poppins', sans-serif;  /* Para títulos y elementos destacados */
--font-secondary: 'Inter', sans-serif;   /* Para contenido principal */
--font-mono: 'SFMono-Regular', monospace; /* Para código */
```

### Jerarquía Tipográfica

```css
/* Títulos */
h1, .h1 { font-size: 3rem; font-weight: 800; line-height: 1.2; }
h2, .h2 { font-size: 2.25rem; font-weight: 700; line-height: 1.3; }
h3, .h3 { font-size: 1.5rem; font-weight: 600; line-height: 1.4; }

/* Contenido */
p { font-size: 1rem; line-height: 1.6; }
small { font-size: 0.875rem; }
```

### Uso Recomendado

- **Poppins**: Para títulos, botones y elementos que requieren impacto visual
- **Inter**: Para párrafos, contenido principal y texto largo
- **SF Mono**: Para bloques de código, datos técnicos y elementos monospace

## Efectos Glassmorphism

### Componentes Glass

```css
.glass-card {
    background: var(--glass-bg-2);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid var(--glass-border);
    border-radius: var(--radius-xl);
    box-shadow: var(--glass-shadow);
    transition: var(--transition-normal);
}

.glass-nav {
    background: var(--glass-bg-1);
    backdrop-filter: blur(16px);
    border: 1px solid var(--glass-border);
}
```

### Efectos Hover

```css
.glass-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 15px 40px rgba(0, 0, 0, 0.12);
    border-color: rgba(255, 255, 255, 0.2);
}
```

### Mejores Prácticas para Glassmorphism

1. **Fondos adecuados**: Usar sobre imágenes o gradientes para mejor efecto
2. **Contraste**: Asegurar que el texto sea legible sobre fondos glass
3. **Capas**: Combinar con sombras y bordes para profundidad
4. **Transparencia**: Ajustar niveles de opacidad según el contexto

## Componentes Reutilizables

### Botones

```html
<!-- Botón Primario -->
<a href="#" class="btn btn-primary">
    <i class="fas fa-rocket"></i>
    Acción Principal
</a>

<!-- Botón Secundario -->
<a href="#" class="btn btn-secondary">
    <i class="fas fa-info"></i>
    Acción Secundaria
</a>

<!-- Botón Glass -->
<a href="#" class="btn btn-glass">
    <i class="fas fa-star"></i>
    Acción Glass
</a>
```

### Tarjetas

```html
<!-- Tarjeta Estándar -->
<div class="card">
    <h3 class="card-title">Título de Tarjeta</h3>
    <p class="card-text">Contenido de la tarjeta con información relevante.</p>
</div>

<!-- Tarjeta Glass -->
<div class="glass-card">
    <h3>Título Glass</h3>
    <p>Contenido con efecto glassmorphism avanzado.</p>
</div>
```

### Alertas

```html
<div class="alert alert-primary">
    <i class="fas fa-info-circle"></i>
    <span>Información importante para el usuario.</span>
</div>

<div class="alert alert-success">
    <i class="fas fa-check-circle"></i>
    <span>Operación completada con éxito.</span>
</div>
```

### Badges

```html
<span class="badge badge-primary">Nuevo</span>
<span class="badge badge-success">Activo</span>
<span class="badge badge-warning">Pendiente</span>
<span class="badge badge-danger">Error</span>
```

### Barra de Navegación

```html
<nav class="navbar" id="navbar">
    <div class="nav-content">
        <a href="#" class="logo">
            <div class="logo-icon">N</div>
            <span>NovaGravity</span>
        </a>
        <div class="nav-links">
            <a href="#inicio" class="nav-link active">Inicio</a>
            <a href="#caracteristicas" class="nav-link">Características</a>
            <a href="#precios" class="nav-link">Precios</a>
        </div>
        <a href="#contacto" class="btn btn-nav btn-primary">
            <i class="fas fa-rocket"></i>
            Contactar
        </a>
    </div>
</nav>
```

## Sistema de Animaciones

### Animaciones Básicas

```css
@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(30px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}
```

### Clases de Animación

```html
<!-- Elemento con fadeIn -->
<div class="fade-in">Contenido que se desvanece</div>

<!-- Elemento con fadeInUp -->
<div class="fade-in-up">Contenido que aparece desde abajo</div>

<!-- Elemento con scroll animation -->
<div class="scroll-animate">Contenido que anima al hacer scroll</div>
```

### Animaciones JavaScript

```javascript
// Typewriter effect
NovaGravityAnimations.typeWriter(element, "Texto a escribir", 50);

// Counter animation
NovaGravityAnimations.animateCounter(element, 1000, 2000);

// Initialize all animations
new NovaGravityAnimations();
```

### Efectos Interactivos

1. **Floating Elements**: Elementos decorativos que responden al movimiento del mouse
2. **Parallax**: Efecto de profundidad al hacer scroll
3. **3D Cards**: Tarjetas con efecto 3D al mover el mouse
4. **Button Hover**: Efectos avanzados de hover en botones
5. **Scroll Animations**: Animaciones basadas en la posición de scroll

## Guía de Implementación

### 1. Estructura Básica HTML

```html
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NovaGravity</title>
    <link rel="stylesheet" href="css/design-system.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
</head>
<body>
    <!-- Contenido aquí -->
    <script src="js/animations.js"></script>
</body>
</html>
```

### 2. Implementación de Componentes

#### Barra de Navegación

```html
<nav class="navbar" id="navbar">
    <div class="nav-content">
        <a href="#" class="logo">
            <div class="logo-icon">N</div>
            <span>NovaGravity</span>
        </a>
        <div class="nav-links">
            <a href="#hero" class="nav-link active">Inicio</a>
            <a href="#features" class="nav-link">Características</a>
            <a href="#pricing" class="nav-link">Precios</a>
        </div>
        <a href="#contact" class="btn btn-primary">
            <i class="fas fa-rocket"></i>
            Empezar
        </a>
    </div>
</nav>
```

#### Sección Hero con Glassmorphism

```html
<section class="hero">
    <div class="floating-element"></div>
    <div class="floating-element"></div>

    <div class="container">
        <div class="hero-content">
            <div class="hero-text">
                <h1>Título Principal</h1>
                <p>Descripción del producto o servicio.</p>
                <div class="btn-group">
                    <a href="#" class="btn btn-primary">CTA Principal</a>
                    <a href="#" class="btn btn-secondary">CTA Secundario</a>
                </div>
            </div>
            <div class="hero-image">
                <div class="glass-card">
                    <img src="image.jpg" alt="Descripción">
                    <h3>Título Card</h3>
                    <p>Descripción del card.</p>
                </div>
            </div>
        </div>
    </div>
</section>
```

#### Sección de Características

```html
<section class="features-section">
    <div class="container">
        <div class="section-header">
            <div class="section-subtitle">Características</div>
            <h2 class="section-title">Lo que ofrecemos</h2>
            <p class="section-description">Descripción de las características principales.</p>
        </div>

        <div class="grid grid-3">
            <div class="feature-card scroll-animate">
                <div class="feature-icon">
                    <i class="fas fa-rocket"></i>
                </div>
                <h3>Característica 1</h3>
                <p>Descripción de la característica.</p>
            </div>

            <div class="feature-card scroll-animate">
                <div class="feature-icon">
                    <i class="fas fa-brain"></i>
                </div>
                <h3>Característica 2</h3>
                <p>Descripción de la característica.</p>
            </div>

            <div class="feature-card scroll-animate">
                <div class="feature-icon">
                    <i class="fas fa-chart-line"></i>
                </div>
                <h3>Característica 3</h3>
                <p>Descripción de la característica.</p>
            </div>
        </div>
    </div>
</section>
```

### 3. Inicialización de JavaScript

```javascript
// Inicializar todas las animaciones
document.addEventListener('DOMContentLoaded', () => {
    new NovaGravityAnimations();

    // Inicializar tooltips
    NovaGravityAnimations.initTooltips();

    // Inicializar scroll to top
    NovaGravityAnimations.initScrollToTop();
});
```

## Mejores Prácticas

### 1. Rendimiento

- **Optimizar imágenes**: Usar formatos modernos como WebP y comprimir adecuadamente
- **Lazy loading**: Implementar carga diferida para imágenes y componentes no críticos
- **Minificar recursos**: CSS y JavaScript minificados para producción
- **Cache**: Configurar cache adecuado para recursos estáticos

### 2. Accesibilidad

- **Contraste**: Asegurar suficiente contraste entre texto y fondo
- **Semántica HTML**: Usar elementos semánticos adecuados
- **ARIA**: Implementar atributos ARIA cuando sea necesario
- **Teclado**: Asegurar que todas las interacciones funcionen con teclado

### 3. Responsividad

- **Mobile-first**: Diseñar pensando primero en dispositivos móviles
- **Breakpoints**: Usar breakpoints lógicos basados en contenido
- **Testing**: Probar en diferentes dispositivos y tamaños de pantalla
- **Touch targets**: Asegurar tamaños adecuados para elementos interactivos

### 4. Mantenibilidad

- **Componentes modulares**: Crear componentes reutilizables y aislados
- **Documentación**: Mantener documentación actualizada
- **Nomenclatura**: Usar nombres semánticos y consistentes
- **Organización**: Estructura clara de archivos y directorios

### 5. Animaciones

- **Duración**: Mantener animaciones cortas (200-500ms)
- **Easing**: Usar curvas de aceleración naturales
- **Rendimiento**: Preferir transform y opacity sobre otras propiedades
- **Reduced motion**: Respetar preferencias de usuario para movimiento reducido

## Estructura de Archivos Recomendada

```
project/
├── css/
│   ├── design-system.css      # Sistema de diseño principal
│   ├── components/             # Componentes específicos
│   └── utilities/              # Utilidades y helpers
├── js/
│   ├── animations.js          # Biblioteca de animaciones
│   ├── components/             # Componentes JS
│   └── main.js                 # Script principal
├── images/                     # Imágenes optimizadas
├── fonts/                      # Fuentes personalizadas
└── index.html                   # Página principal
```

## Conclusión

El sistema de diseño de NovaGravity proporciona una base sólida para crear interfaces modernas, profesionales y coherentes. Con su enfoque en glassmorphism, animaciones fluidas y componentes reutilizables, permite desarrollar aplicaciones web visualmente impactantes sin sacrificar usabilidad o rendimiento.

Para implementaciones personalizadas o extensiones del sistema, se recomienda mantener la coherencia con los principios de diseño establecidos y seguir las mejores prácticas descritas en esta documentación.