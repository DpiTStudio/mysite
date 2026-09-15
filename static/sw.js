/**
 * DPIT-CMS Service Worker v1.0
 * 
 * Стратегия кеширования:
 * - Статические ресурсы: Cache First (быстрая загрузка)
 * - HTML страницы: Network First (актуальный контент)
 * - Оффлайн-фолбек: показываем кешированную главную
 */

const CACHE_NAME = 'dpit-cms-v1';
const STATIC_CACHE = 'dpit-static-v1';

// Ресурсы для предварительного кеширования (app shell)
const PRECACHE_URLS = [
    '/',
    '/static/css/root.css',
    '/static/css/style.css',
    '/static/js/script.js',
    '/static/images/favicon.ico',
];

// Расширения которые кешируем стратегией Cache First
const STATIC_EXTENSIONS = ['.css', '.js', '.woff', '.woff2', '.ttf', '.ico', '.png', '.jpg', '.jpeg', '.webp', '.svg'];

// ——————————————————————————————————————
// INSTALL: предзагрузка app shell
// ——————————————————————————————————————
self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(STATIC_CACHE).then(cache => {
            // Кешируем что можем — игнорируем ошибки отдельных файлов
            return Promise.allSettled(
                PRECACHE_URLS.map(url => cache.add(url).catch(() => {}))
            );
        }).then(() => self.skipWaiting())
    );
});

// ——————————————————————————————————————
// ACTIVATE: удаляем старые кеши
// ——————————————————————————————————————
self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames
                    .filter(name => name !== CACHE_NAME && name !== STATIC_CACHE)
                    .map(name => caches.delete(name))
            );
        }).then(() => self.clients.claim())
    );
});

// ——————————————————————————————————————
// FETCH: логика ответа на запросы
// ——————————————————————————————————————
self.addEventListener('fetch', event => {
    const { request } = event;
    const url = new URL(request.url);

    // Пропускаем: другие домены, POST, admin, API, HTMX
    if (
        url.origin !== self.location.origin ||
        request.method !== 'GET' ||
        url.pathname.startsWith('/admin/') ||
        url.pathname.startsWith('/captcha/') ||
        url.pathname.startsWith('/cart/') ||
        request.headers.get('HX-Request') ||
        request.headers.get('X-Requested-With')
    ) {
        return; // Без SW — нативная загрузка
    }

    const isStatic = STATIC_EXTENSIONS.some(ext => url.pathname.endsWith(ext));

    if (isStatic) {
        // Cache First: сначала кеш, потом сеть, потом кешируем новое
        event.respondWith(
            caches.match(request).then(cached => {
                if (cached) return cached;
                return fetch(request).then(response => {
                    if (response.ok) {
                        const clone = response.clone();
                        caches.open(STATIC_CACHE).then(cache => cache.put(request, clone));
                    }
                    return response;
                });
            })
        );
    } else {
        // Network First: сначала сеть, при ошибке — кеш
        event.respondWith(
            fetch(request)
                .then(response => {
                    if (response.ok) {
                        const clone = response.clone();
                        caches.open(CACHE_NAME).then(cache => cache.put(request, clone));
                    }
                    return response;
                })
                .catch(() => {
                    return caches.match(request).then(cached => {
                        if (cached) return cached;
                        // Фолбек на главную
                        return caches.match('/');
                    });
                })
        );
    }
});
