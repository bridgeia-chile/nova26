// Animations & Interactive Elements Library for NovaGravity
// Features: Scroll Reveal, Accordion, Hover Effects, Floating Animations, Smooth Transitions

// ============================================
// 1. Scroll Reveal Animations
// ============================================
class ScrollReveal {
    constructor() {
        this.elements = [];
        this.init();
    }

    init() {
        // Auto-detect elements with data-scroll-reveal attribute
        document.querySelectorAll('[data-scroll-reveal]').forEach(el => {
            this.elements.push(el);
            el.style.opacity = '0';
            el.style.transform = 'translateY(20px)';
            el.style.transition = 'opacity 0.6s cubic-bezier(0.215, 0.610, 0.355, 1), transform 0.6s cubic-bezier(0.215, 0.610, 0.355, 1)';
        });

        window.addEventListener('scroll', this.handleScroll.bind(this));
        window.addEventListener('resize', this.handleScroll.bind(this));

        // Initial check
        this.handleScroll();
    }

    handleScroll() {
        const triggerBottom = window.innerHeight * 0.85;

        this.elements.forEach(el => {
            const elementTop = el.getBoundingClientRect().top;

            if (elementTop < triggerBottom) {
                el.style.opacity = '1';
                el.style.transform = 'translateY(0)';
            }
        });
    }

    // Add element manually
    addElement(element, options = {}) {
        const { delay = 0, direction = 'up' } = options;
        element.style.opacity = '0';
        element.style.transition = `opacity 0.6s ease ${delay}ms, transform 0.6s ease ${delay}ms`;

        switch(direction) {
            case 'up': element.style.transform = 'translateY(20px)'; break;
            case 'down': element.style.transform = 'translateY(-20px)'; break;
            case 'left': element.style.transform = 'translateX(-20px)'; break;
            case 'right': element.style.transform = 'translateX(20px)'; break;
        }

        this.elements.push(element);
    }
}

// ============================================
// 2. Accordion Component
// ============================================
class Accordion {
    constructor(containerSelector) {
        this.container = typeof containerSelector === 'string'
            ? document.querySelector(containerSelector)
            : containerSelector;
        this.init();
    }

    init() {
        if (!this.container) return;

        const items = this.container.querySelectorAll('.accordion-item');
        items.forEach(item => {
            const header = item.querySelector('.accordion-header');
            const content = item.querySelector('.accordion-content');
            const icon = item.querySelector('.accordion-icon');

            // Set initial state
            content.style.maxHeight = '0';
            content.style.overflow = 'hidden';
            content.style.transition = 'max-height 0.3s ease, padding 0.3s ease';

            header.addEventListener('click', () => {
                const isOpen = content.style.maxHeight !== '0px';

                // Close all other items
                items.forEach(otherItem => {
                    if (otherItem !== item) {
                        otherItem.querySelector('.accordion-content').style.maxHeight = '0px';
                        otherItem.querySelector('.accordion-icon').textContent = '+ ';
                    }
                });

                // Toggle current item
                if (isOpen) {
                    content.style.maxHeight = '0px';
                    if (icon) icon.textContent = '+ ';
                } else {
                    content.style.maxHeight = content.scrollHeight + 'px';
                    if (icon) icon.textContent = '− ';
                }
            });
        });
    }

    static createFAQ(selector, faqData) {
        const container = typeof selector === 'string'
            ? document.querySelector(selector)
            : selector;

        if (!container) return;

        container.innerHTML = faqData.map((item, index) => `
            <div class="accordion-item" data-scroll-reveal>
                <div class="accordion-header">
                    <span class="accordion-icon">+ </span>
                    <h3>${item.question}</h3>
                </div>
                <div class="accordion-content">
                    <p>${item.answer}</p>
                </div>
            </div>
        `).join('');

        return new Accordion(container);
    }
}

// ============================================
// 3. Advanced Hover Effects
// ============================================
class HoverEffects {
    static init() {
        // Button hover effects
        document.querySelectorAll('.btn-hover, button, [data-hover]').forEach(btn => {
            btn.addEventListener('mouseenter', (e) => {
                const rect = e.target.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;

                e.target.style.setProperty('--hover-x', `${x}px`);
                e.target.style.setProperty('--hover-y', `${y}px`);
                e.target.classList.add('hover-effect-active');
            });

            btn.addEventListener('mouseleave', (e) => {
                e.target.classList.remove('hover-effect-active');
            });
        });

        // Card hover effects
        document.querySelectorAll('.card-hover, .agent-card, .glass-card').forEach(card => {
            card.addEventListener('mousemove', (e) => {
                const rect = card.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;
                const centerX = rect.width / 2;
                const centerY = rect.height / 2;

                const rotateX = (centerY - y) / 20;
                const rotateY = (x - centerX) / 20;

                card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale(1.02)`;
            });

            card.addEventListener('mouseleave', () => {
                card.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) scale(1)';
            });
        });
    }

    static applyGradientHover(selector) {
        document.querySelectorAll(selector).forEach(el => {
            el.style.backgroundSize = '200% auto';
            el.style.transition = 'background-position 0.5s ease';

            el.addEventListener('mouseenter', () => {
                el.style.backgroundPosition = 'right center';
            });

            el.addEventListener('mouseleave', () => {
                el.style.backgroundPosition = 'left center';
            });
        });
    }
}

// ============================================
// 4. Floating Animations (PODER, RTIC, C45 Methods)
// ============================================
class FloatingAnimations {
    constructor() {
        this.elements = [];
        this.methods = {
            PODER: this.applyPODER.bind(this),
            RTIC: this.applyRTIC.bind(this),
            C45: this.applyC45.bind(this)
        };
    }

    // PODER: Parabolic Organic Dynamic Elevation Rotation
    applyPODER(element, options = {}) {
        const { speed = 6, amplitude = 20, rotation = 5 } = options;

        element.style.willChange = 'transform';
        element.style.animation = `poder-float ${speed}s ease-in-out infinite`;

        const style = document.createElement('style');
        style.textContent = `
            @keyframes poder-float {
                0%, 100% {
                    transform: translateY(0) rotate(${rotation}deg);
                }
                50% {
                    transform: translateY(-${amplitude}px) rotate(-${rotation}deg);
                }
            }
        `;
        document.head.appendChild(style);
    }

    // RTIC: Rotational Time-Independent Circular
    applyRTIC(element, options = {}) {
        const { radius = 30, duration = 8 } = options;

        element.style.willChange = 'transform';
        element.style.animation = `rtic-orbit ${duration}s linear infinite`;

        const style = document.createElement('style');
        style.textContent = `
            @keyframes rtic-orbit {
                0% {
                    transform: translateX(${radius}px) rotate(0deg);
                }
                25% {
                    transform: translateY(${radius}px) rotate(90deg);
                }
                50% {
                    transform: translateX(-${radius}px) rotate(180deg);
                }
                75% {
                    transform: translateY(-${radius}px) rotate(270deg);
                }
                100% {
                    transform: translateX(${radius}px) rotate(360deg);
                }
            }
        `;
        document.head.appendChild(style);
    }

    // C45: Chaotic 45-degree Multi-axis
    applyC45(element, options = {}) {
        const { intensity = 15, speed = 4 } = options;

        element.style.willChange = 'transform';
        element.style.animation = `c45-chaos ${speed}s ease-in-out infinite`;

        const style = document.createElement('style');
        style.textContent = `
            @keyframes c45-chaos {
                0% {
                    transform: translate(-${intensity}px, ${intensity}px) rotate(45deg);
                }
                25% {
                    transform: translate(${intensity}px, ${intensity}px) rotate(-45deg);
                }
                50% {
                    transform: translate(${intensity}px, -${intensity}px) rotate(45deg);
                }
                75% {
                    transform: translate(-${intensity}px, -${intensity}px) rotate(-45deg);
                }
                100% {
                    transform: translate(-${intensity}px, ${intensity}px) rotate(45deg);
                }
            }
        `;
        document.head.appendChild(style);
    }

    // Apply floating animation to element
    apply(element, method = 'PODER', options = {}) {
        if (this.methods[method]) {
            this.methods[method](element, options);
            this.elements.push({ element, method, options });
        }
    }

    // Apply to multiple elements with selector
    applyToSelector(selector, method = 'PODER', options = {}) {
        document.querySelectorAll(selector).forEach(el => {
            this.apply(el, method, options);
        });
    }
}

// ============================================
// 5. Smooth Section Transitions
// ============================================
class SmoothTransitions {
    constructor() {
        this.currentSection = null;
        this.transitioning = false;
        this.init();
    }

    init() {
        // Handle navigation links
        document.querySelectorAll('a[href^="#"], .nav-item').forEach(link => {
            link.addEventListener('click', (e) => {
                if (link.getAttribute('href') && link.getAttribute('href').startsWith('#')) {
                    e.preventDefault();
                    const targetId = link.getAttribute('href');
                    this.transitionTo(targetId);
                }
            });
        });

        // View transitions API (modern browsers)
        if (document.startViewTransition) {
            this.useViewTransitions = true;
        }
    }

    async transitionTo(target) {
        if (this.transitioning) return;
        this.transitioning = true;

        const targetElement = document.querySelector(target);
        if (!targetElement) {
            this.transitioning = false;
            return;
        }

        if (this.useViewTransitions) {
            await document.startViewTransition(() => {
                targetElement.scrollIntoView({ behavior: 'smooth' });
            }).finished;
        } else {
            // Fallback animation
            document.body.style.overflow = 'hidden';
            const overlay = document.createElement('div');
            overlay.style.position = 'fixed';
            overlay.style.top = '0';
            overlay.style.left = '0';
            overlay.style.width = '100vw';
            overlay.style.height = '100vh';
            overlay.style.background = 'var(--bg-dark)';
            overlay.style.zIndex = '9999';
            overlay.style.opacity = '0';
            overlay.style.transition = 'opacity 0.5s ease';
            document.body.appendChild(overlay);

            // Force reflow
            overlay.getBoundingClientRect();
            overlay.style.opacity = '1';

            await new Promise(resolve => setTimeout(resolve, 300));
            targetElement.scrollIntoView({ behavior: 'smooth' });

            overlay.style.opacity = '0';
            await new Promise(resolve => setTimeout(resolve, 300));
            overlay.remove();
            document.body.style.overflow = '';
        }

        this.transitioning = false;
    }

    // Fade between sections
    static fadeTransition(oldSection, newSection, duration = 500) {
        return new Promise(resolve => {
            oldSection.style.transition = `opacity ${duration}ms ease`;
            oldSection.style.opacity = '0';

            newSection.style.opacity = '0';
            newSection.style.display = 'block';

            setTimeout(() => {
                newSection.style.transition = `opacity ${duration}ms ease`;
                newSection.style.opacity = '1';
                oldSection.style.display = 'none';
                resolve();
            }, 50);
        });
    }
}

// ============================================
// Utility: Apply All Animations
// ============================================
function initNovaAnimations() {
    // Initialize all animation systems
    const scrollReveal = new ScrollReveal();
    const hoverEffects = new HoverEffects();
    const floatingAnimations = new FloatingAnimations();
    const smoothTransitions = new SmoothTransitions();

    // Apply hover effects
    hoverEffects.init();

    // Add scroll reveal to key elements
    document.querySelectorAll('.agent-card, .info-pill, .glass-card, .model-config-card').forEach(el => {
        scrollReveal.addElement(el, { delay: Math.random() * 200 });
    });

    // Apply floating animations to background blobs
    const blobs = document.querySelectorAll('.blob');
    if (blobs.length >= 3) {
        floatingAnimations.apply(blobs[0], 'PODER', { speed: 8, amplitude: 30 });
        floatingAnimations.apply(blobs[1], 'RTIC', { radius: 25, duration: 10 });
        floatingAnimations.apply(blobs[2], 'C45', { intensity: 20, speed: 6 });
    }

    // Enhanced button effects
    document.querySelectorAll('button, [data-hover]').forEach(btn => {
        btn.classList.add('btn-hover');
    });

    console.log('NovaGravity Animations Initialized');

    return {
        scrollReveal,
        hoverEffects,
        floatingAnimations,
        smoothTransitions
    };
}

// Export for module usage
export {
    ScrollReveal,
    Accordion,
    HoverEffects,
    FloatingAnimations,
    SmoothTransitions,
    initNovaAnimations
};

// Auto-initialize if not a module
autoInit();
function autoInit() {
    // Check if we're in a module environment
    if (typeof module !== 'undefined' && module.exports) {
        return; // Don't auto-init if used as module
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initNovaAnimations);
    } else {
        initNovaAnimations();
    }
}