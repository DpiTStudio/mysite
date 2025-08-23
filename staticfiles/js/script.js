// Увеличение изображений при клике
document.addEventListener('DOMContentLoaded', function() {
    const images = document.querySelectorAll('.gallery img, .img-thumbnail');
    
    images.forEach(img => {
        img.addEventListener('click', function() {
            this.classList.toggle('enlarged');
            if (this.classList.contains('enlarged')) {
                this.style.transform = 'scale(1.5)';
                this.style.zIndex = '1000';
            } else {
                this.style.transform = 'scale(1)';
                this.style.zIndex = '1';
            }
        });
    });
    
    // Ленивая загрузка изображений
    if ('IntersectionObserver' in window) {
        const lazyImages = document.querySelectorAll('img[data-src]');
        
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.removeAttribute('data-src');
                    imageObserver.unobserve(img);
                }
            });
        });
        
        lazyImages.forEach(img => imageObserver.observe(img));
    }
});