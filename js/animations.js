/**
 * NovaGravity Animations & Interactions Library
 * Advanced animations and interactive components for modern web interfaces
 */

class NovaGravityAnimations {
    constructor() {
        this.init();
    }

    init() {
        // Initialize all animations and interactions
        this.initPreloader();
        this.initNavbar();
        this.initSmoothScrolling();
        this.initScrollAnimations();
        this.initFloatingElements();
        this.initButtonEffects();
        this.initParallaxEffects();
        this.initIntersectionObservers();
    }

    /**
     * Preloader animation
     */
    initPreloader() {
        window.addEventListener('load', () => {
            const preloader = document.getElementById('preloader');
            if (preloader) {
                setTimeout(() => {
                    preloader.classList.add('hidden');
                    document.body.style.overflow = 'auto';
                }, 1000);
            }
        });
    }

    /**
     * Navbar scroll effect
     */
    initNavbar() {
        const navbar = document.getElementById('navbar');
        if (navbar) {
            window.addEventListener('scroll', () => {
                if (window.scrollY > 50) {
                    navbar.classList.add('scrolled');
                } else {
                    navbar.classList.remove('scrolled');
                }
            });
        }
    }

    /**
     * Smooth scrolling for anchor links
     */
    initSmoothScrolling() {
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const targetId = this.getAttribute('href');
                if (targetId === '#') return;

                const targetElement = document.querySelector(targetId);
                if (targetElement) {
                    window.scrollTo({
                        top: targetElement.offsetTop - 80,
                        behavior: 'smooth'
                    });
                }
            });
        });
    }

    /**
     * Scroll-based animations
     */
    initScrollAnimations() {
        const scrollElements = document.querySelectorAll('.scroll-animate');

        const elementInView = (el, dividend = 1) => {
            const elementTop = el.getBoundingClientRect().top;
            return elementTop <= (window.innerHeight || document.documentElement.clientHeight) / dividend;
        };

        const displayScrollElement = (element) => {
            element.classList.add('scrolled');
        };

        const hideScrollElement = (element) => {
            element.classList.remove('scrolled');
        };

        const handleScrollAnimation = () => {
            scrollElements.forEach((el) => {
                if (elementInView(el, 1.25)) {
                    displayScrollElement(el);
                } else {
                    hideScrollElement(el);
                }
            });
        };

        window.addEventListener('scroll', () => {
            handleScrollAnimation();
        });

        // Initial check
        handleScrollAnimation();
    }

    /**
     * Interactive floating elements
     */
    initFloatingElements() {
        const floatingElements = document.querySelectorAll('.floating-element');

        if (floatingElements.length > 0) {
            window.addEventListener('mousemove', (e) => {
                const mouseX = e.clientX / window.innerWidth;
                const mouseY = e.clientY / window.innerHeight;

                floatingElements.forEach((element, index) => {
                    const speed = 0.05 + (index * 0.02);
                    const x = (mouseX - 0.5) * 50 * speed;
                    const y = (mouseY - 0.5) * 50 * speed;

                    // Preserve existing transforms (like from parallax)
                    const currentTransform = element.style.transform || '';
                    const hasTranslate = currentTransform.includes('translateY');

                    if (!hasTranslate) {
                        element.style.transform = `translate(${x}px, ${y}px) ${currentTransform}`;
                    }
                });
            });
        }
    }

    /**
     * Button hover and click effects
     */
    initButtonEffects() {
        document.querySelectorAll('.btn, .button').forEach(btn => {
            btn.addEventListener('mouseenter', () => {
                if (!btn.classList.contains('btn-glass')) {
                    btn.style.transform = 'translateY(-3px)';
                }
            });

            btn.addEventListener('mouseleave', () => {
                btn.style.transform = 'translateY(0)';
            });

            btn.addEventListener('mousedown', () => {
                btn.style.transform = 'translateY(1px)';
            });

            btn.addEventListener('mouseup', () => {
                btn.style.transform = 'translateY(-3px)';
            });
        });
    }

    /**
     * Parallax effects for background elements
     */
    initParallaxEffects() {
        window.addEventListener('scroll', () => {
            const scrolled = window.pageYOffset;

            // Parallax for floating elements
            const floatingElements = document.querySelectorAll('.floating-element');
            floatingElements.forEach((element, index) => {
                const speed = 0.5 + (index * 0.1);
                const currentTransform = element.style.transform || '';

                // Extract existing translate values
                const translateMatch = currentTransform.match(/translate\(([^)]+)\)/);
                let existingTranslate = '';

                if (translateMatch) {
                    existingTranslate = translateMatch[0];
                }

                element.style.transform = `${existingTranslate} translateY(${scrolled * speed}px)`;
            });

            // Parallax for hero background
            const hero = document.querySelector('.hero');
            if (hero) {
                hero.style.backgroundPositionY = `-${scrolled * 0.3}px`;
            }
        });
    }

    /**
     * Intersection Observer for animations
     */
    initIntersectionObservers() {
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');

                    // Animate feature cards sequentially
                    if (entry.target.classList.contains('feature-card')) {
                        const index = Array.from(entry.target.parentNode.children).indexOf(entry.target);
                        entry.target.style.animationDelay = `${index * 0.2}s`;
                    }
                }
            });
        }, observerOptions);

        // Observe feature cards
        document.querySelectorAll('.feature-card, .pricing-card, .glass-card').forEach(card => {
            observer.observe(card);
        });
    }

    /**
     * Animate glass card 3D effects
     */
    initGlassCardEffects() {
        document.querySelectorAll('.glass-card').forEach(card => {
            const cardInner = card.querySelector('.glass-card-inner') || card;

            card.addEventListener('mousemove', (e) => {
                const xAxis = (window.innerWidth / 2 - e.pageX) / 25;
                const yAxis = (window.innerHeight / 2 - e.pageY) / 25;
                cardInner.style.transform = `rotateY(${xAxis}deg) rotateX(${yAxis}deg)`;
            });

            card.addEventListener('mouseenter', () => {
                cardInner.style.transition = 'none';
            });

            card.addEventListener('mouseleave', () => {
                cardInner.style.transform = 'rotateY(0) rotateX(0)';
                cardInner.style.transition = 'transform 0.5s ease';
            });
        });
    }

    /**
     * Typewriter effect for text
     */
    static typeWriter(element, text, speed = 50) {
        let i = 0;
        element.innerHTML = '';

        const typing = () => {
            if (i < text.length) {
                element.innerHTML += text.charAt(i);
                i++;
                setTimeout(typing, speed);
            }
        };

        typing();
    }

    /**
     * Counter animation
     */
    static animateCounter(element, end, duration = 2000) {
        let start = 0;
        const range = end - start;
        const increment = end > start ? 1 : -1;
        const stepTime = Math.abs(Math.floor(duration / range));

        const timer = setInterval(() => {
            start += increment;
            element.textContent = start;

            if ((increment > 0 && start >= end) || (increment < 0 && start <= end)) {
                clearInterval(timer);
                element.textContent = end;
            }
        }, stepTime);
    }

    /**
     * Scroll to top button
     */
    static initScrollToTop() {
        const scrollToTopBtn = document.createElement('button');
        scrollToTopBtn.className = 'btn btn-primary scroll-to-top';
        scrollToTopBtn.innerHTML = '<i class="fas fa-arrow-up"></i>';
        scrollToTopBtn.style.position = 'fixed';
        scrollToTopBtn.style.bottom = '2rem';
        scrollToTopBtn.style.right = '2rem';
        scrollToTopBtn.style.zIndex = '1000';
        scrollToTopBtn.style.display = 'none';

        document.body.appendChild(scrollToTopBtn);

        window.addEventListener('scroll', () => {
            if (window.pageYOffset > 300) {
                scrollToTopBtn.style.display = 'block';
            } else {
                scrollToTopBtn.style.display = 'none';
            }
        });

        scrollToTopBtn.addEventListener('click', () => {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }

    /**
     * Initialize tooltip system
     */
    static initTooltips() {
        document.querySelectorAll('[data-tooltip]').forEach(element => {
            const tooltipText = element.getAttribute('data-tooltip');
            const tooltip = document.createElement('div');
            tooltip.className = 'tooltip';
            tooltip.textContent = tooltipText;
            tooltip.style.position = 'absolute';
            tooltip.style.background = 'var(--dark-900)';
            tooltip.style.color = 'white';
            tooltip.style.padding = '0.5rem 1rem';
            tooltip.style.borderRadius = 'var(--radius-md)';
            tooltip.style.fontSize = '0.875rem';
            tooltip.style.zIndex = '1000';
            tooltip.style.opacity = '0';
            tooltip.style.transition = 'opacity 0.3s';
            tooltip.style.pointerEvents = 'none';
            tooltip.style.whiteSpace = 'nowrap';

            element.style.position = 'relative';
            element.appendChild(tooltip);

            element.addEventListener('mouseenter', () => {
                const rect = element.getBoundingClientRect();
                tooltip.style.left = `${rect.width / 2}px`;
                tooltip.style.top = `-40px`;
                tooltip.style.transform = 'translateX(-50%)';
                tooltip.style.opacity = '1';
            });

            element.addEventListener('mouseleave', () => {
                tooltip.style.opacity = '0';
            });
        });
    }
}

// Initialize animations when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new NovaGravityAnimations();
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = NovaGravityAnimations;
}