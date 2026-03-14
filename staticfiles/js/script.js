// Улучшенные эффекты для сайта
document.addEventListener('DOMContentLoaded', function() {
    // 1. Preloader
    const preloader = document.getElementById('preloader');
    if (preloader) {
        const hidePreloader = () => {
            if (preloader.style.opacity !== '0') {
                preloader.style.opacity = '0';
                preloader.style.visibility = 'hidden';
            }
        };
        
        window.addEventListener('load', function() {
            setTimeout(hidePreloader, 500);
        });
        
        // Safety net to hide preloader even if external resources fail
        setTimeout(hidePreloader, 2000);
    }

    // 2. Scroll Progress Bar
    const progressBar = document.getElementById('scroll-progress');
    if (progressBar) {
        window.addEventListener('scroll', () => {
            const windowScroll = document.body.scrollTop || document.documentElement.scrollTop;
            const height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
            const scrolled = (windowScroll / height) * 100;
            progressBar.style.width = scrolled + '%';
        });
    }

    // 3. Эффект скролла для навигации и шапки
    const navbar = document.querySelector('.navbar');
    const mainHeader = document.querySelector('.main-header');
    let lastScroll = 0;
    
    if (navbar) {
        window.addEventListener('scroll', function() {
            const currentScroll = window.pageYOffset;
            
            if (currentScroll > 50) {
                navbar.classList.add('scrolled');
                
                // Smart header: hide top bar when scrolling down
                if (mainHeader) {
                    if (currentScroll > lastScroll && currentScroll > 150) {
                        mainHeader.classList.add('hide-top-bar');
                    } else if (currentScroll < lastScroll) {
                        mainHeader.classList.remove('hide-top-bar');
                    }
                }
            } else {
                navbar.classList.remove('scrolled');
                if (mainHeader) mainHeader.classList.remove('hide-top-bar');
            }
            lastScroll = currentScroll <= 0 ? 0 : currentScroll;
        });
    }
    
    // 4. Анимация появления элементов при скролле
    const animateOnScroll = function() {
        const elements = document.querySelectorAll('.animate-up, .animate-left, .animate-right, .animate-scale, .glass-card, .card, .glass-card-premium');
        elements.forEach(el => {
            const rect = el.getBoundingClientRect();
            // Порог появления: 10% элемента должно быть видно (или сразу если они уже в области видимости)
            const isVisible = rect.top < (window.innerHeight - 50) && rect.bottom > 0;
            if (isVisible) {
                el.classList.add('animate-active');
            }
        });
    };
    
    // Начальные стили для анимаций заданы в CSS, но для надежности:
    window.addEventListener('scroll', animateOnScroll);
    // Небольшая задержка для плавного старта
    setTimeout(animateOnScroll, 100);

    // Функция для инициализации динамических элементов
    function initDynamicElements(root) {
        // 5. Увеличение изображений
        root.querySelectorAll('.gallery img, .img-thumbnail, .card-img-top').forEach(img => {
            img.addEventListener('click', function(e) {
                e.stopPropagation();
                this.classList.toggle('enlarged');
                if (this.classList.contains('enlarged')) {
                    this.style.transform = 'scale(1.1)';
                    this.style.zIndex = '100';
                } else {
                    this.style.transform = 'scale(1)';
                    this.style.zIndex = '1';
                }
            });
        });
        
        // 6. Плавная прокрутка
        root.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function(e) {
                const href = this.getAttribute('href');
                if (href !== '#' && href !== '') {
                    const target = document.querySelector(href);
                    if (target) {
                        e.preventDefault();
                        target.scrollIntoView({
                            behavior: 'smooth'
                        });
                    }
                }
            });
        });
        
        // 7. Ripple эффект
        root.querySelectorAll('.btn, .nav-link').forEach(button => {
            button.addEventListener('mousedown', function(e) {
                const ripple = document.createElement('span');
                const rect = this.getBoundingClientRect();
                const size = Math.max(rect.width, rect.height);
                const x = e.clientX - rect.left - size / 2;
                const y = e.clientY - rect.top - size / 2;
                
                ripple.style.width = ripple.style.height = size + 'px';
                ripple.style.left = x + 'px';
                ripple.style.top = y + 'px';
                ripple.classList.add('ripple');
                
                this.appendChild(ripple);
                setTimeout(() => ripple.remove(), 600);
            });
        });

        // 12. Fix clickable parent dropdowns on desktop
        root.querySelectorAll('.dropdown-toggle.clickable-parent').forEach(function(el) {
            el.addEventListener('click', function(e) {
                if (window.innerWidth >= 992 && this.href && this.href !== '#' && !this.href.endsWith('#')) {
                    // Prevent bootstrap default behaviour
                    window.location.href = this.href;
                }
            });
        });
    }

    // Инициализация для исходного документа
    initDynamicElements(document);

    // Инициализация для элементов, загруженных через HTMX
    document.body.addEventListener('htmx:load', function(e) {
        initDynamicElements(e.detail.elt);
        // Запускаем анимацию для нового контента с небольшой задержкой (чтобы DOM успел обновиться)
        setTimeout(animateOnScroll, 100);
        // Для подстраховки проверяем скролл
        window.scrollTo(0, 0); 
    });

    // 8. Стили для Ripple (если не добавлены)
    if (!document.getElementById('extra-styles')) {
        const style = document.createElement('style');
        style.id = 'extra-styles';
        style.textContent = `
            .ripple {
                position: absolute;
                border-radius: 50%;
                background: rgba(255, 255, 255, 0.3);
                transform: scale(0);
                animation: ripple-animation 0.6s linear;
                pointer-events: none;
            }
            @keyframes ripple-animation {
                to { transform: scale(4); opacity: 0; }
            }
            .animate-active { opacity: 1 !important; transform: translateY(0) !important; }
        `;
        document.head.appendChild(style);
    }

    // 9. Theme Switcher
    const themeToggleBtn = document.getElementById('themeToggleBtn');
    const themeIcon = document.getElementById('themeIcon');
    
    // Check saved theme or system preference
    const savedTheme = localStorage.getItem('theme');
    const prefersLight = window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches;
    
    if (savedTheme === 'light' || (!savedTheme && prefersLight)) {
        document.body.classList.add('light-mode');
        if (themeIcon) {
            themeIcon.classList.remove('bi-moon-stars');
            themeIcon.classList.add('bi-sun');
        }
    }
    
    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', function(e) {
            e.preventDefault();
            document.body.classList.toggle('light-mode');
            
            if (document.body.classList.contains('light-mode')) {
                localStorage.setItem('theme', 'light');
                themeIcon.classList.remove('bi-moon-stars');
                themeIcon.classList.add('bi-sun');
            } else {
                localStorage.setItem('theme', 'dark');
                themeIcon.classList.remove('bi-sun');
                themeIcon.classList.add('bi-moon-stars');
            }
        });
    }

    // 10. Configure HTMX to send Django CSRF token
    document.body.addEventListener('htmx:configRequest', (event) => {
        const csrfTokenMatch = document.cookie.match(/csrftoken=([^;]+)/);
        if (csrfTokenMatch) {
            event.detail.headers['X-CSRFToken'] = csrfTokenMatch[1];
        }
    });

    // 11. Включаем View Transitions API для красивых SPA переходов HTMX
    if (typeof htmx !== 'undefined') {
        htmx.config.globalViewTransitions = true;
    }

    // ============================================================
    // ИННОВАЦИОННЫЕ УЛУЧШЕНИЯ v2.0
    // Для отката: git revert HEAD (после коммита)
    // ============================================================

    // 12. 3D Tilt Effect — наклон карточек при движении мыши
    function init3DTilt(root) {
        root.querySelectorAll('.card, .glass-card, .glass-card-premium').forEach(card => {
            // Пропускаем мобильные устройства (pointer: coarse)
            if (window.matchMedia('(pointer: coarse)').matches) return;

            card.addEventListener('mousemove', (e) => {
                const rect = card.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;
                const centerX = rect.width / 2;
                const centerY = rect.height / 2;
                const rotateX = ((y - centerY) / centerY) * 8;
                const rotateY = ((centerX - x) / centerX) * 8;
                card.style.transform = `perspective(900px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-6px) scale(1.01)`;
                // Динамичный highlight — следует за курсором
                const percentX = (x / rect.width) * 100;
                const percentY = (y / rect.height) * 100;
                card.style.background = `radial-gradient(circle at ${percentX}% ${percentY}%, rgba(255,255,255,0.07), transparent 60%)`;
            });

            card.addEventListener('mouseleave', () => {
                card.style.transform = '';
                card.style.background = '';
            });
        });
    }

    init3DTilt(document);

    document.body.addEventListener('htmx:load', (e) => {
        init3DTilt(e.detail.elt);
    });

    // 13. Active Nav Item — подсвечиваем текущий раздел в навигации
    (function markActiveNav() {
        const currentPath = window.location.pathname;
        document.querySelectorAll('.main-nav-item').forEach(item => {
            const link = item.querySelector('a.nav-link');
            if (!link) return;
            const href = link.getAttribute('href');
            if (!href || href === '#') return;
            if (currentPath.startsWith(href) && href !== '/') {
                item.classList.add('active');
            } else if (href === '/' && currentPath === '/') {
                item.classList.add('active');
            }
        });
    })();

    // ============================================================
    // 14. Scroll-to-Top Button — кнопка "наверх"
    // ============================================================
    (function initScrollToTop() {
        // Создаём кнопку программно
        const btn = document.createElement('button');
        btn.id = 'scroll-to-top-btn';
        btn.setAttribute('aria-label', 'Прокрутить наверх');
        btn.setAttribute('title', 'Наверх');
        btn.innerHTML = '<i class="bi bi-arrow-up"></i>';
        btn.style.cssText = [
            'position: fixed',
            'bottom: 2rem',
            'right: 2rem',
            'width: 48px',
            'height: 48px',
            'border-radius: 50%',
            'border: none',
            'background: var(--gradient-premium, linear-gradient(135deg,#6c63ff,#48cae4))',
            'color: #fff',
            'font-size: 1.2rem',
            'cursor: pointer',
            'z-index: 9999',
            'box-shadow: 0 4px 20px rgba(108,99,255,0.45)',
            'opacity: 0',
            'visibility: hidden',
            'transform: translateY(10px)',
            'transition: opacity 0.3s ease, visibility 0.3s ease, transform 0.3s ease',
            'display: flex',
            'align-items: center',
            'justify-content: center',
        ].join(';');
        document.body.appendChild(btn);

        // Показываем/скрываем в зависимости от позиции скролла
        const toggleVisibility = () => {
            if (window.scrollY > 300) {
                btn.style.opacity = '1';
                btn.style.visibility = 'visible';
                btn.style.transform = 'translateY(0)';
            } else {
                btn.style.opacity = '0';
                btn.style.visibility = 'hidden';
                btn.style.transform = 'translateY(10px)';
            }
        };

        window.addEventListener('scroll', toggleVisibility, { passive: true });

        btn.addEventListener('click', () => {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });

        // Небольшой hover-эффект
        btn.addEventListener('mouseenter', () => {
            btn.style.filter = 'brightness(1.15)';
            btn.style.transform = 'translateY(-3px)';
        });
        btn.addEventListener('mouseleave', () => {
            btn.style.filter = '';
            btn.style.transform = window.scrollY > 300 ? 'translateY(0)' : 'translateY(10px)';
        });
    })();
});
