# NovaGravity Animations System Documentation

## Overview

The NovaGravity Animations System provides professional-grade animations and interactive elements for the dashboard interface. It includes five main components:

1. **Scroll Reveal Animations** - Elements fade in as users scroll
2. **Accordion Component** - Interactive FAQ and collapsible sections
3. **Advanced Hover Effects** - Ripple effects, 3D tilts, and gradients
4. **Floating Animations** - Three unique methods (PODER, RTIC, C45)
5. **Smooth Transitions** - Section transitions and view changes

## Installation

The system is automatically included in the main dashboard. To use it in other pages:

```html
<!-- Include the CSS -->
<link rel="stylesheet" href="style.min.css">

<!-- Include the JavaScript -->
<script src="animations.min.js" type="module"></script>
```

## Usage Guide

### 1. Scroll Reveal Animations

Add `data-scroll-reveal` attribute to any element:

```html
<div class="card" data-scroll-reveal>
    This will fade in when scrolled into view
</div>
```

**Options:**
- `data-delay="100"` - Add delay in milliseconds
- `data-direction="up|down|left|right"` - Set animation direction (default: up)

**JavaScript API:**
```javascript
const scrollReveal = new ScrollReveal();
scrollReveal.addElement(document.getElementById('my-element'), {
    delay: 200,
    direction: 'left'
});
```

### 2. Accordion Component

**HTML Structure:**
```html
<div class="accordion-item">
    <div class="accordion-header">
        <span class="accordion-icon">+ </span>
        <h3>Question Title</h3>
    </div>
    <div class="accordion-content">
        <p>Answer content goes here</p>
    </div>
</div>
```

**JavaScript Initialization:**
```javascript
// Automatic initialization
const accordion = new Accordion('#accordion-container');

// Create FAQ programmatically
const faqData = [
    { question: "Question 1", answer: "Answer 1" },
    { question: "Question 2", answer: "Answer 2" }
];
Accordion.createFAQ('#faq-container', faqData);
```

### 3. Advanced Hover Effects

**Button Hover Effects:**
```html
<button class="btn-hover">Hover Me</button>
```

**Card Hover Effects:**
```html
<div class="card-hover">
    Content with 3D tilt effect on hover
</div>
```

**Gradient Effects:**
```html
<button class="gradient-btn">Gradient Button</button>
```

### 4. Floating Animations

Three animation methods available:

**PODER (Parabolic Organic Dynamic Elevation Rotation):**
```javascript
const floatingAnimations = new FloatingAnimations();
floatingAnimations.apply(document.getElementById('element'), 'PODER', {
    speed: 6,
    amplitude: 20,
    rotation: 5
});
```

**RTIC (Rotational Time-Independent Circular):**
```javascript
floatingAnimations.apply(element, 'RTIC', {
    radius: 30,
    duration: 8
});
```

**C45 (Chaotic 45-degree Multi-axis):**
```javascript
floatingAnimations.apply(element, 'C45', {
    intensity: 15,
    speed: 4
});
```

**Apply to multiple elements:**
```javascript
floatingAnimations.applyToSelector('.floating-elements', 'PODER');
```

### 5. Smooth Transitions

**Section Transitions:**
```javascript
const transitions = new SmoothTransitions();
transitions.transitionTo('#target-section');
```

**Fade Transitions:**
```javascript
await SmoothTransitions.fadeTransition(oldSection, newSection);
```

**View Transitions (Modern Browsers):**
```javascript
if (document.startViewTransition) {
    document.startViewTransition(() => {
        updateDOM();
    });
}
```

## CSS Classes Reference

### Animation Classes
- `.section-transition` - Fade in animation
- `.section-transition.visible` - Visible state
- `.btn-hover` - Button with ripple effect
- `.card-hover` - Card with 3D tilt
- `.gradient-btn` - Button with gradient animation
- `.floating-poder` - PODER animation
- `.floating-rtic` - RTIC animation
- `.floating-c45` - C45 animation

### Utility Classes
- `.accordion-item` - Accordion container
- `.accordion-header` - Clickable header
- `.accordion-content` - Expandable content
- `.accordion-icon` - Plus/minus icon

## Performance Considerations

1. **will-change**: Used on animated elements to hint browser
2. **transform-style: preserve-3d**: Maintains 3D context
3. **backface-visibility**: Prevents flickering
4. **Hardware Acceleration**: All animations use GPU-accelerated properties
5. **Debounced Scroll Events**: Scroll handlers are optimized

## Browser Compatibility

- Chrome 60+
- Firefox 55+
- Safari 11+
- Edge 79+
- Mobile browsers with ES6 support

## Customization

### Global Settings

Modify CSS variables in `:root`:

```css
:root {
    --accent: #00e5ff; /* Main accent color */
    --accent-glow: rgba(0, 229, 255, 0.3); /* Glow effect */
}
```

### Animation Parameters

Override default animation parameters:

```javascript
// Scroll Reveal
const scrollReveal = new ScrollReveal();
scrollReveal.triggerPoint = 0.9; // 90% from top

// Floating Animations
floatingAnimations.apply(element, 'PODER', {
    speed: 8, // Slower
    amplitude: 30, // Higher bounce
    rotation: 10 // More rotation
});
```

## Examples

### Creating an Animated Dashboard

```html
<div class="dashboard">
    <!-- Header with floating animation -->
    <header class="floating-poder">
        <h1>Dashboard</h1>
    </header>

    <!-- Cards with scroll reveal -->
    <div class="cards-grid">
        <div class="card card-hover" data-scroll-reveal data-delay="100">
            <h3>Card 1</h3>
        </div>
        <div class="card card-hover" data-scroll-reveal data-delay="200">
            <h3>Card 2</h3>
        </div>
    </div>

    <!-- FAQ Section -->
    <div id="faq-section"></div>
</div>

<script>
// Initialize animations
const animations = initNovaAnimations();

// Create FAQ
Accordion.createFAQ('#faq-section', [
    { question: "How to use?", answer: "Just follow the instructions..." },
    { question: "Is it free?", answer: "Yes, completely free!" }
]);
</script>
```

### Advanced Button with Multiple Effects

```html
<button class="btn-hover gradient-btn"
        data-hover
        style="--gradient-start: #ff00cc; --gradient-end: #3333ff;">
    <i class="fas fa-rocket"></i> Launch
</button>
```

## Integration with Existing Components

The animation system integrates seamlessly with existing NovaGravity components:

- **Agent Cards**: Automatic hover effects and scroll reveal
- **Navigation**: Smooth transitions between views
- **Modals**: Fade in/out animations
- **Settings**: Accordion for organized configuration

## Troubleshooting

**Animations not working?**
- Check browser console for errors
- Ensure `type="module"` is set on script tag
- Verify CSS is properly loaded
- Check for JavaScript errors in other scripts

**Performance issues?**
- Reduce number of simultaneous animations
- Increase delays between elements
- Use simpler animation methods on mobile
- Consider reducing animation complexity

## API Reference

### ScrollReveal Class

```javascript
const scrollReveal = new ScrollReveal();
scrollReveal.addElement(element, options);
```

**Options:**
- `delay`: Number (ms) - Animation delay
- `direction`: String ('up', 'down', 'left', 'right')

### Accordion Class

```javascript
const accordion = new Accordion(containerSelector);
Accordion.createFAQ(selector, faqData);
```

**faqData format:**
```javascript
[
    { question: "Question", answer: "Answer" },
    ...
]
```

### HoverEffects Class

```javascript
HoverEffects.init(); // Auto-initialize
HoverEffects.applyGradientHover(selector);
```

### FloatingAnimations Class

```javascript
const floating = new FloatingAnimations();
floating.apply(element, method, options);
floating.applyToSelector(selector, method, options);
```

**Methods:** 'PODER', 'RTIC', 'C45'

### SmoothTransitions Class

```javascript
const transitions = new SmoothTransitions();
transitions.transitionTo(targetSelector);
SmoothTransitions.fadeTransition(oldEl, newEl, duration);
```

## Best Practices

1. **Use sparingly**: Too many animations can be distracting
2. **Performance first**: Test on low-end devices
3. **Accessibility**: Ensure animations don't interfere with usability
4. **Consistency**: Use similar animation styles throughout
5. **Purpose**: Each animation should have a clear purpose

## License

MIT License - Free for personal and commercial use.

## Support

For issues or questions, contact the NovaGravity team or open an issue on GitHub.

---

**Version**: 1.0.0
**Last Updated**: March 9, 2026
**Author**: NovaGravity Team