"""
Настройки Django проекта DPIT-CMS.
Этот файл содержит все основные конфигурации проекта, разделённые на логические секции
для удобства чтения и поддержки. Все комментарии написаны на русском языке.
"""

# ------------------------------------------------------------
# Библиотеки
# ------------------------------------------------------------
import os
from pathlib import Path
import importlib.util

# Путь к корню проекта
BASE_DIR = Path(__file__).resolve().parent.parent

# ------------------------------------------------------------
# Безопасность
# ------------------------------------------------------------
# Секретный ключ
SECRET_KEY = 'django-insecure-8*2@x&p^+-j7s=e!k_v$i3(4l%z)t1w5y#9_q^0r+2m'
# Режим отладки – НЕ включать в продакшн!
DEBUG = True
# Доступные хосты по умолчанию порт 4234
ALLOWED_HOSTS = [
    '*',
    '127.0.0.1:4234',
    'localhost:4234',
    'dpit-cms.ru:4234',
    'www.dpit-cms.ru:4234',
]

# ------------------------------------------------------------
# Приложения (INSTALLED_APPS)
# ------------------------------------------------------------
INSTALLED_APPS = [
    # Темы
    "jazzmin",
    # Основные приложения
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",  # Для sitemap.xml
    "captcha",  # Капча
    # Мои приложения
    "main.apps.MainConfig", # Главная страница
    "news.apps.NewsConfig", # Новости
    "portfolio.apps.PortfolioConfig", # Портфолио
    "reviews.apps.ReviewsConfig", # Отзывы
    "logfiles.apps.LogfilesConfig", # Логи
    "accounts.apps.AccountsConfig", # Аккаунты
    "tickets.apps.TicketsConfig", # Тикеты
    "mail.apps.MailConfig", # Почта
    "services.apps.ServicesConfig", # Услуги
    "cart.apps.CartConfig", # Корзина
    "knowledge_base.apps.KnowledgeBaseConfig", # База знаний
    "tinymce", # Редактор
    
]

# ------------------------------------------------------------
# Middleware
# ------------------------------------------------------------
MIDDLEWARE = [
    # Основные middleware
    "django.middleware.security.SecurityMiddleware", # Безопасность
    "django.contrib.sessions.middleware.SessionMiddleware", # Сессии
    "django.middleware.common.CommonMiddleware", # Общие настройки
    "django.middleware.csrf.CsrfViewMiddleware", # CSRF
    "django.contrib.auth.middleware.AuthenticationMiddleware", # Аутентификация
    "django.contrib.messages.middleware.MessageMiddleware", # Сообщения
    "django.middleware.clickjacking.XFrameOptionsMiddleware", # Защита от кликджекинга
]
# Подключаем WhiteNoise, если он установлен (обслуживание статики)
HAS_WHITENOISE = importlib.util.find_spec("whitenoise") is not None
if HAS_WHITENOISE: # Если WhiteNoise установлен
    MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")

# ------------------------------------------------------------
# URL‑конфигурация и шаблоны
# ------------------------------------------------------------
ROOT_URLCONF = "mysite.urls" # Главная страница

TEMPLATES = [
    {
        # Основные шаблоны
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")], # Шаблоны
        "APP_DIRS": True, # Приложения
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug", # Отладка
                "django.template.context_processors.request", # Запрос
                "mysite.context_processors.season_theme", # Тема
                "django.contrib.auth.context_processors.auth", # Аутентификация
                "django.contrib.messages.context_processors.messages", # Сообщения
                "main.context_processors.main_context", # Главная страница
                "news.context_processors.latest_news", # Новости
                "portfolio.context_processors.latest_portfolio", # Портфолио
                "reviews.context_processors.latest_reviews", # Отзывы
                "cart.context_processors.cart", # Корзина
            ],
        },
    },
]

# Главная страница
WSGI_APPLICATION = "mysite.wsgi.application"

# ------------------------------------------------------------
# База данных
# ------------------------------------------------------------
DATABASES = {
    # Основная база данных
    "default": {
        "ENGINE": "django.db.backends.sqlite3", # SQLite
        "NAME": BASE_DIR / "db.sqlite3", # Путь к базе данных
    }
}


# ------------------------------------------------------------
# Валидация паролей
# ------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    # Основные валидаторы
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"}, # Проверка схожести пароля
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"}, # Минимальная длина пароля
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"}, # Проверка на частые пароли
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"}, # Проверка на числовые пароли
]

# ------------------------------------------------------------
# Интернационализация
# ------------------------------------------------------------
LANGUAGE_CODE = "ru-ru" # Русский язык
TIME_ZONE = "Europe/Moscow" # Московское время
USE_I18N = True # Интернационализация
USE_TZ = True # Часовые пояса

# ------------------------------------------------------------
# Статические и медиа‑файлы
# ------------------------------------------------------------
STATIC_URL = "/static/" # URL для статических файлов
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")] # Путь к статическим файлам
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles") # Путь к статическим файлам

MEDIA_URL = "/media/" # URL для медиа‑файлов
MEDIA_ROOT = os.path.join(BASE_DIR, "media") # Путь к медиа‑файлам

# Хранилища (по умолчанию и для staticfiles)
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"}, # Хранилище по умолчанию
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"}, # Хранилище для статических файлов
}
# В продакшене используем манифесты для кеширования
if not DEBUG: # Если DEBUG выключен
    # В продакшене используем CompressedManifestStaticFilesStorage без дополнительных опций,
    # чтобы избежать ошибки "unexpected keyword argument 'manifest_strict'".
    STORAGES["staticfiles"] = {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"
    }

# ------------------------------------------------------------
# Пользовательская модель
# ------------------------------------------------------------
AUTH_USER_MODEL = "accounts.User" # Пользовательская модель

# ------------------------------------------------------------
# Настройки капчи
# ------------------------------------------------------------
CAPTCHA_CHALLENGE_FUNCT = "captcha.helpers.random_char_challenge" # Функция для генерации капчи
CAPTCHA_LENGTH = 3 
CAPTCHA_TIMEOUT = 5
CAPTCHA_IMAGE_SIZE = (200, 80) # Размеры картинки (ширина, высота)
CAPTCHA_FONT_SIZE = 48 # Размер шрифта на картинке
SECURE_CONTENT_TYPE_NOSNIFF = False

# ------------------------------------------------------------
# Jazzmin – админ‑панель
# ------------------------------------------------------------
JAZZMIN_SETTINGS = {
    # Основные настройки
    "site_title": "DPIT-CMS Admin", # Название админ-панели
    "site_header": "DPIT-CMS", # Заголовок админ-панели
    "site_brand": "DPIT-CMS", # Бренд админ-панели
    "site_brand_small": "DPIT", # Маленький бренд админ-панели
    "site_logo_classes": "img-circle", # Классы для логотипа
    "site_logo": "images/logo.png", # Логотип админ-панели
    "site_footer": "DPIT-CMS", # Футер админ-панели
    "menu_open_first_child": True, # Открывать первый пункт меню
    "welcome_sign": "Добро пожаловать в админ-панель DPIT-CMS", # Приветственное сообщение
    "copyright": "DPIT-CMS", # Копирайт
    "show_ui_builder": True, # Показывать UI builder
    "changeform_format": "horizontal_tabs", # Формат изменения формы
    "changeform_format_overrides": {
        "auth.user": "collapsible", # Формат изменения формы для пользователя
        "auth.group": "vertical_tabs", # Формат изменения формы для группы
        "admin.logentry": "vertical_tabs", # Формат изменения формы для лога
    },
    "use_google_fonts_cdn": True, # Использовать Google Fonts CDN
    "show_sidebar": True, # Показывать боковую панель
    "navigation_expanded": True, # Разворачивать боковую панель
    "hide_apps": [], # Скрывать приложения
    "hide_models": [], # Скрывать модели
    "order_with_respect_to": [
        "main", # Главная
        "knowledge_base", # База знаний
        "news", # Новости
        "portfolio", # Портфолио
        "services", # Услуги
        "reviews", # Отзывы
        "tickets", # Тикеты
        "mail", # Почта
        "accounts", # Аккаунты
        "logfiles", # Логи
    ],
    "custom_links": {
        # Главная
        "main": [{
            "name": "Вернуться на сайт",
            "url": "/",
            "icon": "fas fa-home",
            "new_window": True,
        }]
    },
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "main.SiteSettings": "fas fa-cog",
        "main.Page": "fas fa-file-alt",
        "knowledge_base.Category": "fas fa-folder",
        "knowledge_base.Article": "fas fa-book",
        "news.NewsCategory": "fas fa-folder",
        "news.News": "fas fa-newspaper",
        "news.Comment": "fas fa-comments",
        "portfolio.PortfolioCategory": "fas fa-folder-open",
        "portfolio.Portfolio": "fas fa-images",
        "services.Service": "fas fa-concierge-bell",
        "services.ServiceOrder": "fas fa-file-invoice-dollar",
        "reviews.Review": "fas fa-star",
        "tickets.Ticket": "fas fa-ticket-alt",
        "tickets.TicketMessage": "fas fa-comment-dots",
        "mail.Mail": "fas fa-envelope",
        "logfiles.LogFile": "fas fa-file-alt",
        "logfiles.LogBackup": "fas fa-archive",
        "accounts.User": "fas fa-user-circle",
        "admin.LogEntry": "fas fa-history",
    },
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",
    "related_modal_active": False,
    "custom_css": "css/admin_custom.css",
    "custom_js": None,
    "menu": [
        {"name": "Главная", "icon": "fas fa-home", "url": "/", "new_window": True},
        {"app": "main", "icon": "fas fa-cogs"},
        {"app": "knowledge_base", "icon": "fas fa-book"},
        {"app": "news", "icon": "fas fa-newspaper"},
        {"app": "portfolio", "icon": "fas fa-images"},
        {"app": "services", "icon": "fas fa-concierge-bell"},
        {"app": "reviews", "icon": "fas fa-star"},
        {"app": "tickets", "icon": "fas fa-ticket-alt"},
        {"app": "mail", "icon": "fas fa-envelope"},
        {"app": "accounts", "icon": "fas fa-users"},
        {"app": "logfiles", "icon": "fas fa-file-alt"},
        {"model": "admin.LogEntry", "label": "История действий", "icon": "fas fa-history"},
    ],
}

JAZZMIN_UI_TWEAKS = {
    # Настройки внешнего вида
    "navbar_small_text": True, # Маленький текст в навигации
    "footer_small_text": True, # Маленький текст в футере
    "body_small_text": True, # Маленький текст в теле
    "brand_small_text": True, # Маленький текст бренда
    "brand_colour": "navbar-dark", # Цвет бренда
    "accent": "accent-primary", # Акцентный цвет
    "navbar": "navbar-dark", # Цвет навигации
    "no_navbar_border": True, # Без рамки навигации
    "navbar_fixed": False, # Фиксированная навигация
    "layout_boxed": False, # Боксовый макет
    "footer_fixed": True, # Фиксированный футер
    "sidebar_fixed": True, # Фиксированная боковая панель
    "sidebar": "sidebar-dark-primary", # Цвет боковой панели
    "sidebar_nav_small_text": True, # Маленький текст в боковой панели
    "sidebar_disable_expand": True, # Отключить разворачивание боковой панели
    "sidebar_nav_child_indent": True, # Отступ у дочерних элементов
    "sidebar_nav_compact_style": True, # Компактный стиль боковой панели
    "sidebar_nav_legacy_style": True, # Старый стиль боковой панели
    "sidebar_nav_flat_style": True, # Плоский стиль боковой панели
    "theme": "darkly", # Тема
    "dark_mode_theme": None, # Темная тема
    "button_classes": {
        "primary": "btn-primary", # Основная кнопка
        "secondary": "btn-secondary", # Вторичная кнопка
        "info": "btn-info", # Информационная кнопка
        "warning": "btn-warning", # Предупреждающая кнопка
        "danger": "btn-danger", # Опасная кнопка
        "success": "btn-success", # Успешная кнопка
    },
}

# ------------------------------------------------------------
# CSRF и безопасность
# ------------------------------------------------------------
CSRF_TRUSTED_ORIGINS = [
    "https://dpit-cms.ru", # Доверенные источники
    "http://dpit-cms.ru", # Доверенные источники
    "https://www.dpit-cms.ru", # Доверенные источники
    "http://www.dpit-cms.ru", # Доверенные источники
    "http://localhost:4234", # Доверенные источники
    "http://127.0.0.1:4234", # Доверенные источники
    "http://localhost:8000", # Доверенные источники
    "http://127.0.0.1:8000", # Доверенные источники
]
CSRF_COOKIE_SAMESITE = "Lax" # Безопасность CSRF
SESSION_COOKIE_SAMESITE = "Lax" # Безопасность сессий
CSRF_COOKIE_SECURE = not DEBUG # Безопасность CSRF
SESSION_COOKIE_SECURE = not DEBUG # Безопасность сессий
SECURE_SSL_REDIRECT = False # Перенаправление на HTTPS
SECURE_HSTS_SECONDS = 31536000 if not DEBUG and SECURE_SSL_REDIRECT else 0 # Безопасность HSTS
SECURE_HSTS_INCLUDE_SUBDOMAINS = not DEBUG and SECURE_SSL_REDIRECT # Безопасность HSTS
SECURE_HSTS_PRELOAD = not DEBUG and SECURE_SSL_REDIRECT # Безопасность HSTS
SECURE_BROWSER_XSS_FILTER = True # Безопасность XSS
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https") # Безопасность прокси
X_FRAME_OPTIONS = "DENY" # Безопасность XSS

# ------------------------------------------------------------
# Логирование
# ------------------------------------------------------------
LOGGING = {
    # Версия конфигурации логирования
    "version": 1,
    # Отключить существующие логгеры
    "disable_existing_loggers": False,
    # Фильтры
    "filters": {
        # Фильтр для пропуска ошибок "Broken pipe"
        "skip_broken_pipe": {
            "()": "django.utils.log.CallbackFilter",
            "callback": lambda record: "Broken pipe" not in record.getMessage(),
        },
    },
    "formatters": {
        "verbose": {"format": "{levelname} {asctime} {module} {message}", "style": "{"},
        "simple": {"format": "{levelname} {message}", "style": "{"},
    },
    "handlers": {
        "file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": BASE_DIR / "logs" / "django.log",
            "formatter": "verbose",
        },
        "console": {
            "level": "DEBUG" if DEBUG else "INFO",
            "class": "logging.StreamHandler",
            "formatter": "simple",
            "filters": ["skip_broken_pipe"],
        },
    },
    "root": {"handlers": ["console", "file"], "level": "INFO"},
    "loggers": {
        "django": {"handlers": ["console", "file"], "level": "INFO", "propagate": False},
        "django.server": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "news": {"handlers": ["console", "file"], "level": "DEBUG" if DEBUG else "INFO", "propagate": False},
    },
}

# ------------------------------------------------------------
# Кеширование
# ------------------------------------------------------------
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

# ------------------------------------------------------------
# Создание директории для логов (если её нет)
# ------------------------------------------------------------
logs_dir = BASE_DIR / "logs"
if not logs_dir.exists():
    os.makedirs(logs_dir, exist_ok=True)

# ------------------------------------------------------------
# Настройки почты
# ------------------------------------------------------------
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.timeweb.ru"
EMAIL_PORT = 465
EMAIL_USE_SSL = True
EMAIL_HOST_USER = "admin@dpit-cms.ru"
EMAIL_HOST_PASSWORD = "V2Jy*qKeb/j?L6"
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
SERVER_EMAIL = EMAIL_HOST_USER

# ------------------------------------------------------------
# Настройки IMAP (Timeweb)
# ------------------------------------------------------------
IMAP_HOST = "imap.timeweb.ru"
IMAP_PORT = 993
IMAP_USER = EMAIL_HOST_USER
IMAP_PASSWORD = EMAIL_HOST_PASSWORD

# ------------------------------------------------------------
# Celery
# ------------------------------------------------------------
CELERY_BROKER_URL = "redis://localhost:6379/2"
CELERY_RESULT_BACKEND = CELERY_BROKER_URL
CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE

# ------------------------------------------------------------
# Идентификатор корзины в сессии
# ------------------------------------------------------------
CART_SESSION_ID = "cart"

# ------------------------------------------------------------
# Конец файла settings.py
# ------------------------------------------------------------
