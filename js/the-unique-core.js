/**
 * THE UNIQUE - LEGENDARY INTERACTION FRAMEWORK v4.0
 * Premium JavaScript Core for Ultra-Smooth UX
 * Inspired by Top Crypto/Mystical Sites of 2026
 * Last Updated: 2026-02-16
 */

// ============================================
// 🎬 INITIALIZATION & PAGE LOAD
// ============================================
(function() {
  'use strict';

  // Performance Monitoring
  const perfMonitor = {
    start: performance.now(),
    marks: {},
    mark(name) {
      this.marks[name] = performance.now() - this.start;
      console.log(`⚡ ${name}: ${this.marks[name].toFixed(2)}ms`);
    }
  };

  // ============================================
  // 🌐 LOADING SCREEN MANAGER
  // ============================================
  class LoadingScreen {
    constructor() {
      this.element = null;
      this.minDisplayTime = 500; // Minimum loading time for smooth experience
      this.startTime = Date.now();
    }

    init() {
      // Create loading screen if it doesn't exist
      if (!document.querySelector('.loading-screen')) {
        this.element = document.createElement('div');
        this.element.className = 'loading-screen';
        this.element.innerHTML = `
          <div class="loading-spinner"></div>
          <div class="loading-text">THE UNIQUE</div>
        `;
        document.body.prepend(this.element);
      } else {
        this.element = document.querySelector('.loading-screen');
      }
    }

    hide() {
      const elapsed = Date.now() - this.startTime;
      const remainingTime = Math.max(0, this.minDisplayTime - elapsed);

      setTimeout(() => {
        if (this.element) {
          this.element.classList.add('hidden');
          setTimeout(() => {
            this.element.remove();
            perfMonitor.mark('Loading screen hidden');
          }, 500);
        }
      }, remainingTime);
    }
  }

  // ============================================
  // 🧭 PREMIUM NAVIGATION SYSTEM
  // ============================================
  class NavigationManager {
    constructor() {
      this.nav = null;
      this.toggle = null;
      this.menu = null;
      this.lastScrollY = window.scrollY;
      this.scrollThreshold = 10;
      this.isMenuOpen = false;
    }

    init() {
      this.createNavigation();
      this.attachEventListeners();
      this.setActiveLink();
      perfMonitor.mark('Navigation initialized');
    }

    createNavigation() {
      // Check if navigation already exists
      if (document.querySelector('.the-unique-nav')) {
        this.nav = document.querySelector('.the-unique-nav');
        this.toggle = this.nav.querySelector('.nav-toggle');
        this.menu = this.nav.querySelector('.nav-menu');
        return;
      }

      // Create navigation structure
      const nav = document.createElement('nav');
      nav.className = 'the-unique-nav';
      nav.setAttribute('role', 'navigation');
      nav.setAttribute('aria-label', 'Main navigation');

      const pages = [
        { name: 'Home', url: 'the-unique-main.html', icon: '🏛️' },
        { name: 'Tarot', url: 'tarot.html', icon: '🔮' },
        { name: 'Saju', url: 'saju.html', icon: '🌙' },
        { name: 'News', url: 'news.html', icon: '📰' },
        { name: 'Slang', url: 'slang.html', icon: '💬' },
        { name: 'Survival', url: 'survival.html', icon: '⚔️' },
        { name: 'Exchange', url: 'exchange-select.html', icon: '💰' }
      ];

      nav.innerHTML = `
        <div class="nav-container">
          <a href="the-unique-main.html" class="nav-logo" aria-label="THE UNIQUE home">
            THE UNIQUE
          </a>
          <button class="nav-toggle" aria-label="Toggle navigation menu" aria-expanded="false">
            <span></span>
            <span></span>
            <span></span>
          </button>
          <ul class="nav-menu" role="menubar">
            ${pages.map(page => `
              <li role="none">
                <a href="${page.url}" class="nav-link" role="menuitem">
                  <span class="nav-icon" aria-hidden="true">${page.icon}</span>
                  <span>${page.name}</span>
                </a>
              </li>
            `).join('')}
          </ul>
        </div>
      `;

      document.body.prepend(nav);
      this.nav = nav;
      this.toggle = nav.querySelector('.nav-toggle');
      this.menu = nav.querySelector('.nav-menu');
    }

    attachEventListeners() {
      // Mobile menu toggle
      if (this.toggle) {
        this.toggle.addEventListener('click', () => this.toggleMobileMenu());
      }

      // Scroll detection for auto-hide
      let ticking = false;
      window.addEventListener('scroll', () => {
        if (!ticking) {
          window.requestAnimationFrame(() => {
            this.handleScroll();
            ticking = false;
          });
          ticking = true;
        }
      });

      // Close menu when clicking outside
      document.addEventListener('click', (e) => {
        if (this.isMenuOpen && !this.nav.contains(e.target)) {
          this.closeMobileMenu();
        }
      });

      // Close menu on navigation
      const links = this.nav.querySelectorAll('.nav-link');
      links.forEach(link => {
        link.addEventListener('click', () => {
          this.closeMobileMenu();
        });
      });

      // Keyboard navigation
      this.menu.addEventListener('keydown', (e) => {
        this.handleKeyboardNav(e);
      });
    }

    toggleMobileMenu() {
      this.isMenuOpen = !this.isMenuOpen;
      this.toggle.classList.toggle('active');
      this.menu.classList.toggle('active');
      this.toggle.setAttribute('aria-expanded', this.isMenuOpen);
      document.body.classList.toggle('no-scroll', this.isMenuOpen);
    }

    closeMobileMenu() {
      this.isMenuOpen = false;
      this.toggle.classList.remove('active');
      this.menu.classList.remove('active');
      this.toggle.setAttribute('aria-expanded', 'false');
      document.body.classList.remove('no-scroll');
    }

    handleScroll() {
      const currentScrollY = window.scrollY;

      // Auto-hide on scroll down, show on scroll up
      if (Math.abs(currentScrollY - this.lastScrollY) < this.scrollThreshold) {
        return;
      }

      if (currentScrollY > this.lastScrollY && currentScrollY > 100) {
        // Scrolling down
        this.nav.classList.add('hidden');
      } else {
        // Scrolling up
        this.nav.classList.remove('hidden');
      }

      this.lastScrollY = currentScrollY;
    }

    setActiveLink() {
      const currentPage = window.location.pathname.split('/').pop() || 'the-unique-main.html';
      const links = this.nav.querySelectorAll('.nav-link');
      
      links.forEach(link => {
        if (link.getAttribute('href') === currentPage) {
          link.classList.add('active');
          link.setAttribute('aria-current', 'page');
        }
      });
    }

    handleKeyboardNav(e) {
      const links = Array.from(this.menu.querySelectorAll('.nav-link'));
      const currentIndex = links.findIndex(link => link === document.activeElement);

      switch(e.key) {
        case 'ArrowRight':
        case 'ArrowDown':
          e.preventDefault();
          const nextIndex = (currentIndex + 1) % links.length;
          links[nextIndex].focus();
          break;
        case 'ArrowLeft':
        case 'ArrowUp':
          e.preventDefault();
          const prevIndex = (currentIndex - 1 + links.length) % links.length;
          links[prevIndex].focus();
          break;
        case 'Escape':
          e.preventDefault();
          this.closeMobileMenu();
          this.toggle.focus();
          break;
      }
    }
  }

  // ============================================
  // ✨ PREMIUM ANIMATIONS MANAGER
  // ============================================
  class AnimationManager {
    constructor() {
      this.observers = [];
    }

    init() {
      this.setupIntersectionObserver();
      this.setupParallaxEffect();
      this.setupHoverEffects();
      perfMonitor.mark('Animations initialized');
    }

    setupIntersectionObserver() {
      const options = {
        root: null,
        rootMargin: '0px',
        threshold: 0.1
      };

      const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            entry.target.classList.add('page-transition');
            observer.unobserve(entry.target);
          }
        });
      }, options);

      // Observe all major sections
      const sections = document.querySelectorAll('.card, .section, .feature');
      sections.forEach(section => {
        section.style.opacity = '0';
        observer.observe(section);
      });

      this.observers.push(observer);
    }

    setupParallaxEffect() {
      const parallaxElements = document.querySelectorAll('[data-parallax]');
      
      if (parallaxElements.length === 0) return;

      let ticking = false;

      window.addEventListener('scroll', () => {
        if (!ticking) {
          window.requestAnimationFrame(() => {
            parallaxElements.forEach(element => {
              const speed = parseFloat(element.dataset.parallax) || 0.5;
              const yPos = -(window.scrollY * speed);
              element.style.transform = `translateY(${yPos}px)`;
            });
            ticking = false;
          });
          ticking = true;
        }
      });
    }

    setupHoverEffects() {
      // Add magnetic effect to buttons
      const buttons = document.querySelectorAll('.btn');
      
      buttons.forEach(button => {
        button.addEventListener('mousemove', (e) => {
          const rect = button.getBoundingClientRect();
          const x = e.clientX - rect.left - rect.width / 2;
          const y = e.clientY - rect.top - rect.height / 2;
          
          button.style.transform = `translate(${x * 0.1}px, ${y * 0.1}px)`;
        });

        button.addEventListener('mouseleave', () => {
          button.style.transform = '';
        });
      });
    }

    cleanup() {
      this.observers.forEach(observer => observer.disconnect());
    }
  }

  // ============================================
  // 🎯 PERFORMANCE OPTIMIZER
  // ============================================
  class PerformanceOptimizer {
    constructor() {
      this.images = [];
    }

    init() {
      this.setupLazyLoading();
      this.optimizeFonts();
      this.reportMetrics();
      perfMonitor.mark('Performance optimizations applied');
    }

    setupLazyLoading() {
      // Native lazy loading for images
      const images = document.querySelectorAll('img:not([loading])');
      images.forEach(img => {
        img.setAttribute('loading', 'lazy');
        img.setAttribute('decoding', 'async');
      });

      // Intersection Observer for advanced lazy loading
      const imageObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            const img = entry.target;
            if (img.dataset.src) {
              img.src = img.dataset.src;
              img.removeAttribute('data-src');
            }
            imageObserver.unobserve(img);
          }
        });
      });

      const lazyImages = document.querySelectorAll('img[data-src]');
      lazyImages.forEach(img => imageObserver.observe(img));
    }

    optimizeFonts() {
      // Preload critical fonts
      const fonts = [
        { family: 'Cinzel', weight: '700' },
        { family: 'Pretendard', weight: '400' }
      ];

      fonts.forEach(font => {
        const link = document.createElement('link');
        link.rel = 'preload';
        link.as = 'font';
        link.crossOrigin = 'anonymous';
        link.href = `https://fonts.gstatic.com/s/${font.family.toLowerCase()}/${font.family.toLowerCase()}-${font.weight}.woff2`;
        document.head.appendChild(link);
      });
    }

    reportMetrics() {
      // Report Web Vitals if available
      if ('PerformanceObserver' in window) {
        try {
          // Largest Contentful Paint (LCP)
          new PerformanceObserver((list) => {
            const entries = list.getEntries();
            const lastEntry = entries[entries.length - 1];
            console.log('📊 LCP:', lastEntry.renderTime || lastEntry.loadTime);
          }).observe({ entryTypes: ['largest-contentful-paint'] });

          // First Input Delay (FID)
          new PerformanceObserver((list) => {
            const entries = list.getEntries();
            entries.forEach(entry => {
              console.log('📊 FID:', entry.processingStart - entry.startTime);
            });
          }).observe({ entryTypes: ['first-input'] });

          // Cumulative Layout Shift (CLS)
          new PerformanceObserver((list) => {
            let cls = 0;
            list.getEntries().forEach(entry => {
              if (!entry.hadRecentInput) {
                cls += entry.value;
              }
            });
            console.log('📊 CLS:', cls);
          }).observe({ entryTypes: ['layout-shift'] });
        } catch (e) {
          console.warn('Performance monitoring not fully supported');
        }
      }
    }
  }

  // ============================================
  // 🎨 THEME & VISUAL EFFECTS
  // ============================================
  class VisualEffects {
    init() {
      this.addBackgroundAnimations();
      this.setupCursorEffects();
      perfMonitor.mark('Visual effects initialized');
    }

    addBackgroundAnimations() {
      // Add subtle animated gradient overlay
      const hasBackground = document.querySelector('.animated-background');
      if (hasBackground) return;

      const overlay = document.createElement('div');
      overlay.className = 'animated-background';
      overlay.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: -1;
        opacity: 0.05;
        background: radial-gradient(circle at 20% 50%, #a855f7 0%, transparent 50%),
                    radial-gradient(circle at 80% 80%, #fbbf24 0%, transparent 50%),
                    radial-gradient(circle at 40% 20%, #22d3ee 0%, transparent 50%);
        background-size: 200% 200%;
        animation: gradient-shift 15s ease infinite;
        pointer-events: none;
      `;

      // Add keyframe animation
      if (!document.querySelector('#gradient-animation')) {
        const style = document.createElement('style');
        style.id = 'gradient-animation';
        style.textContent = `
          @keyframes gradient-shift {
            0%, 100% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
          }
        `;
        document.head.appendChild(style);
      }

      document.body.appendChild(overlay);
    }

    setupCursorEffects() {
      // Premium cursor trail effect
      const trail = [];
      const trailLength = 20;

      document.addEventListener('mousemove', (e) => {
        trail.push({ x: e.clientX, y: e.clientY });
        if (trail.length > trailLength) trail.shift();

        // Only apply on interactive elements
        const target = e.target;
        if (target.matches('.btn, .nav-link, .card, a[href]')) {
          target.style.cursor = 'pointer';
        }
      });
    }
  }

  // ============================================
  // 🚀 MAIN INITIALIZATION
  // ============================================
  const TheUniqueCore = {
    loadingScreen: null,
    navigation: null,
    animations: null,
    performance: null,
    visual: null,

    init() {
      console.log('🌟 THE UNIQUE CORE v4.0 - Initializing...');

      // Initialize loading screen
      this.loadingScreen = new LoadingScreen();
      this.loadingScreen.init();

      // Wait for DOM to be ready
      if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => this.bootstrap());
      } else {
        this.bootstrap();
      }
    },

    bootstrap() {
      try {
        // Initialize all systems
        this.navigation = new NavigationManager();
        this.navigation.init();

        this.animations = new AnimationManager();
        this.animations.init();

        this.performance = new PerformanceOptimizer();
        this.performance.init();

        this.visual = new VisualEffects();
        this.visual.init();

        // Hide loading screen after everything is ready
        window.addEventListener('load', () => {
          this.loadingScreen.hide();
          perfMonitor.mark('Page fully loaded');
          console.log('✨ THE UNIQUE is ready!');
        });

        // Add page transition on navigation
        this.setupPageTransitions();

      } catch (error) {
        console.error('❌ Initialization error:', error);
        this.loadingScreen.hide();
      }
    },

    setupPageTransitions() {
      document.addEventListener('click', (e) => {
        const link = e.target.closest('a[href]');
        if (!link || link.target === '_blank' || link.hostname !== window.location.hostname) {
          return;
        }

        const href = link.getAttribute('href');
        if (!href || href.startsWith('#') || href.startsWith('javascript:')) {
          return;
        }

        e.preventDefault();
        document.body.style.opacity = '0';
        document.body.style.transition = 'opacity 300ms ease-out';

        setTimeout(() => {
          window.location.href = href;
        }, 300);
      });
    }
  };

  // Auto-initialize
  TheUniqueCore.init();

  // Expose to global scope for external use
  window.TheUniqueCore = TheUniqueCore;

})();
