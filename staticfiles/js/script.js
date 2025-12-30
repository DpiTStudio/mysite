// Улучшенные эффекты для сайта
document.addEventListener('DOMContentLoaded', function() {
    // Эффект скролла для навигации
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        let lastScroll = 0;
        
        window.addEventListener('scroll', function() {
            const currentScroll = window.pageYOffset;
            
            if (currentScroll > 100) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }
            
            lastScroll = currentScroll;
        });
    }
    
    // Увеличение изображений при клике с улучшенной анимацией
    const images = document.querySelectorAll('.gallery img, .img-thumbnail, .card-img-top');
    
    images.forEach(img => {
        img.style.transition = 'transform 0.3s ease, z-index 0.3s ease';
        img.style.cursor = 'pointer';
        
        img.addEventListener('click', function(e) {
            e.stopPropagation();
            this.classList.toggle('enlarged');
            if (this.classList.contains('enlarged')) {
                this.style.transform = 'scale(1.5)';
                this.style.zIndex = '1000';
                this.style.position = 'relative';
            } else {
                this.style.transform = 'scale(1)';
                this.style.zIndex = '1';
            }
        });
        
        // Закрытие при клике вне изображения
        document.addEventListener('click', function(e) {
            if (!img.contains(e.target) && img.classList.contains('enlarged')) {
                img.classList.remove('enlarged');
                img.style.transform = 'scale(1)';
                img.style.zIndex = '1';
            }
        });
    });
    
    // Ленивая загрузка изображений с fade-in эффектом
    if ('IntersectionObserver' in window) {
        const lazyImages = document.querySelectorAll('img[data-src]');
        
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.style.opacity = '0';
                    img.style.transition = 'opacity 0.5s ease';
                    
                    img.onload = function() {
                        this.style.opacity = '1';
                    };
                    
                    img.src = img.dataset.src;
                    img.removeAttribute('data-src');
                    imageObserver.unobserve(img);
                }
            });
        }, {
            rootMargin: '50px'
        });
        
        lazyImages.forEach(img => {
            img.style.opacity = '0';
            imageObserver.observe(img);
        });
    }
    
    // Анимация появления элементов при скролле
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const fadeInObserver = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.animation = 'fadeInUp 0.6s ease-out forwards';
                fadeInObserver.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    // Применяем анимацию к карточкам
    document.querySelectorAll('.card, .news-card, .portfolio-item').forEach(el => {
        el.style.opacity = '0';
        fadeInObserver.observe(el);
    });
    
    // Плавная прокрутка для якорных ссылок
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href !== '#' && href !== '') {
                const target = document.querySelector(href);
                if (target) {
                    e.preventDefault();
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }
        });
    });
    
    // Эффект ripple для кнопок
    document.querySelectorAll('.btn, .nav-link').forEach(button => {
        button.addEventListener('click', function(e) {
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
            
            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
    });
    
    // Добавляем стили для ripple эффекта
    if (!document.getElementById('ripple-styles')) {
        const style = document.createElement('style');
        style.id = 'ripple-styles';
        style.textContent = `
            .btn, .nav-link {
                position: relative;
                overflow: hidden;
            }
            .ripple {
                position: absolute;
                border-radius: 50%;
                background: rgba(255, 255, 255, 0.6);
                transform: scale(0);
                animation: ripple-animation 0.6s ease-out;
                pointer-events: none;
            }
            @keyframes ripple-animation {
                to {
                    transform: scale(4);
                    opacity: 0;
                }
            }
        `;
        document.head.appendChild(style);
    }
});