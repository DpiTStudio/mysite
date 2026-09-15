/* Custom JavaScript for Django Admin DPIT-CMS */

document.addEventListener('DOMContentLoaded', function() {
    // 1. Плавное появление элементов
    const cards = document.querySelectorAll('.card, .small-box');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        
        setTimeout(() => {
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, 100 * index);
    });

    // 2. Улучшение поиска в дашборде (если мы на нем)
    const appSearch = document.getElementById('appSearch');
    if (appSearch) {
        appSearch.addEventListener('focus', function() {
            this.parentElement.style.transform = 'scale(1.05)';
            this.parentElement.style.transition = 'transform 0.3s ease';
        });
        appSearch.addEventListener('blur', function() {
            this.parentElement.style.transform = 'scale(1)';
        });
    }

    // 3. Добавление "живого" эффекта для статистики
    const animateValue = (obj, start, end, duration) => {
        let startTimestamp = null;
        const step = (timestamp) => {
            if (!startTimestamp) startTimestamp = timestamp;
            const progress = Math.min((timestamp - startTimestamp) / duration, 1);
            obj.innerHTML = Math.floor(progress * (end - start) + start);
            if (progress < 1) {
                window.requestAnimationFrame(step);
            }
        };
        window.requestAnimationFrame(step);
    };

    const statsNumbers = document.querySelectorAll('.small-box h3');
    statsNumbers.forEach(num => {
        const val = parseInt(num.innerText);
        if (!isNaN(val) && val > 0) {
            animateValue(num, 0, val, 1500);
        }
    });

    // 4. Твик для сайдбара
    const sidebar = document.querySelector('.main-sidebar');
    if (sidebar) {
        sidebar.addEventListener('mouseenter', () => {
             // Можно добавить эффекты свечения
        });
    }
});
