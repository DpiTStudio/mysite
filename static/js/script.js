// Улучшенные эффекты для сайта
document.addEventListener('DOMContentLoaded', function() {
    // 1. Preloader
    const preloader = document.getElementById('preloader');
    if (preloader) {
        window.addEventListener('load', function() {
            setTimeout(() => {
                preloader.style.opacity = '0';
                preloader.style.visibility = 'hidden';
            }, 500);
        });
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

    // 3. Эффект скролла для навигации
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        window.addEventListener('scroll', function() {
            if (window.pageYOffset > 50) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }
        });
    }
    
    // 4. Анимация появления элементов при скролле
    const animateOnScroll = function() {
        const elements = document.querySelectorAll('.animate-up, .animate-left, .animate-right, .animate-scale, .glass-card, .card, .glass-card-premium');
        elements.forEach(el => {
            const rect = el.getBoundingClientRect();
            // Порог появления: 10% элемента должно быть видно
            const isVisible = rect.top < (window.innerHeight - 100) && rect.bottom > 0;
            if (isVisible) {
                el.classList.add('animate-active');
            }
        });
    };
    
    // Начальные стили для анимаций заданы в CSS, но для надежности:
    window.addEventListener('scroll', animateOnScroll);
    // Небольшая задержка для плавного старта
    setTimeout(animateOnScroll, 100);

    // 5. Увеличение изображений
    const images = document.querySelectorAll('.gallery img, .img-thumbnail, .card-img-top');
    images.forEach(img => {
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
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
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
    document.querySelectorAll('.btn, .nav-link').forEach(button => {
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
});
