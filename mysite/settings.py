"""
Настройки Django проекта DPIT-CMS.
Этот файл содержит все основные конфигурации проекта, разделённые на логические секции
для удобства чтения и поддержки. Все комментарии написаны на русском языке.
"""

# ------------------------------------------------------------
# Библиотеки и переменные окружения
# ------------------------------------------------------------
import os
from pathlib import Path
import environ
import importlib.util

# Инициализация django-environ
env = environ.Env(
    DEBUG=(bool, True)  # По умолчанию DEBUG выключен
)
# Путь к корню проекта
BASE_DIR = Path(__file__).resolve().parent.parent
# Загрузка .env файла
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# ------------------------------------------------------------
# Безопасность
# ------------------------------------------------------------
# Секретный ключ – храните в .env, а не в репозитории
# , default='django-insecure-8*2@x&p^+-j7s=e!k_v$i3(4l%z)t1w5y#9_q^0r+2m'
SECRET_KEY = env('SECRET_KEY')
# Режим отладки – НЕ включать в продакшн!
# DEBUG = env('DEBUG')
DEBUG = env('DEBUG', default=False)
# Доступные хосты по умолчанию порт 4234
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[
    '*',
    '127.0.0.1:4234',
    'localhost:4234',
    'dpit-cms.ru:4234',
    'www.dpit-cms.ru:4234',
    ])
# Добавление IP‑адресов из переменных окружения (если заданы)
if env('INTERNAL_IPS', default=None):
    ALLOWED_HOSTS.extend(env.list('INTERNAL_IPS'))

# ------------------------------------------------------------
# Приложения (INSTALLED_APPS)
# ------------------------------------------------------------
INSTALLED_APPS = [
    "jazzmin",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",  # Для sitemap.xml
    "captcha",  # Капча
    "main.apps.MainConfig",
    "news.apps.NewsConfig",
    "portfolio.apps.PortfolioConfig",
    "reviews.apps.ReviewsConfig",
    "logfiles.apps.LogfilesConfig",
    "accounts.apps.AccountsConfig",
    "tickets.apps.TicketsConfig",
    "mail.apps.MailConfig",
    "services.apps.ServicesConfig",
    "cart.apps.CartConfig",
    "knowledge_base.apps.KnowledgeBaseConfig",
    "tinymce",
]

# ------------------------------------------------------------
# Middleware
# ------------------------------------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
# Подключаем WhiteNoise, если он установлен (обслуживание статики)
HAS_WHITENOISE = importlib.util.find_spec("whitenoise") is not None
if HAS_WHITENOISE:
    MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")

# ------------------------------------------------------------
# URL‑конфигурация и шаблоны
# ------------------------------------------------------------
ROOT_URLCONF = "mysite.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "mysite.context_processors.season_theme",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "main.context_processors.main_context",
                "news.context_processors.latest_news",
                "portfolio.context_processors.latest_portfolio",
                "reviews.context_processors.latest_reviews",
                "cart.context_processors.cart",
            ],
        },
    },
]

WSGI_APPLICATION = "mysite.wsgi.application"

# ------------------------------------------------------------
# База данных
# ------------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
# При наличии DATABASE_URL в .env переопределяем настройки
if env('DATABASE_URL', default=None):
    DATABASES['default'] = env.db('DATABASE_URL')

# ------------------------------------------------------------
# Валидация паролей
# ------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ------------------------------------------------------------
# Интернационализация
# ------------------------------------------------------------
LANGUAGE_CODE = "ru-ru"
TIME_ZONE = "Europe/Moscow"
USE_I18N = True
USE_TZ = True

# ------------------------------------------------------------
# Статические и медиа‑файлы
# ------------------------------------------------------------
STATIC_URL = "/static/"
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# Хранилища (по умолчанию и для staticfiles)
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}
# В продакшене используем манифесты для кеширования
if not DEBUG:
    # В продакшене используем CompressedManifestStaticFilesStorage без дополнительных опций,
    # чтобы избежать ошибки "unexpected keyword argument 'manifest_strict'".
    STORAGES["staticfiles"] = {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"
    }

# ------------------------------------------------------------
# Пользовательская модель
# ------------------------------------------------------------
AUTH_USER_MODEL = "accounts.User"

# ------------------------------------------------------------
# Настройки капчи
# ------------------------------------------------------------
CAPTCHA_CHALLENGE_FUNCT = "captcha.helpers.random_char_challenge"
CAPTCHA_LENGTH = 3
CAPTCHA_TIMEOUT = 5
SECURE_CONTENT_TYPE_NOSNIFF = False

# ------------------------------------------------------------
# Jazzmin – админ‑панель
# ------------------------------------------------------------
JAZZMIN_SETTINGS = {
    "site_title": "DPIT-CMS Admin",
    "site_header": "DPIT-CMS",
    "site_brand": "DPIT-CMS",
    "site_brand_small": "DPIT",
    "site_logo_classes": "img-circle",
    "site_logo": "images/logo.png",
    "site_footer": "DPIT-CMS",
    "menu_open_first_child": True,
    "welcome_sign": "Добро пожаловать в админ-панель DPIT-CMS",
    "copyright": "DPIT-CMS",
    "show_ui_builder": True,
    "changeform_format": "horizontal_tabs",
    "changeform_format_overrides": {
        "auth.user": "collapsible",
        "auth.group": "vertical_tabs",
        "admin.logentry": "vertical_tabs",
    },
    "use_google_fonts_cdn": True,
    "show_sidebar": True,
    "navigation_expanded": True,
    "hide_apps": [],
    "hide_models": [],
    "order_with_respect_to": [
        "main",
        "knowledge_base",
        "news",
        "portfolio",
        "services",
        "reviews",
        "tickets",
        "mail",
        "accounts",
        "logfiles",
    ],
    "custom_links": {
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
    "navbar_small_text": True,
    "footer_small_text": True,
    "body_small_text": True,
    "brand_small_text": True,
    "brand_colour": "navbar-dark",
    "accent": "accent-primary",
    "navbar": "navbar-dark",
    "no_navbar_border": True,
    "navbar_fixed": False,
    "layout_boxed": False,
    "footer_fixed": True,
    "sidebar_fixed": True,
    "sidebar": "sidebar-dark-primary",
    "sidebar_nav_small_text": True,
    "sidebar_disable_expand": True,
    "sidebar_nav_child_indent": True,
    "sidebar_nav_compact_style": True,
    "sidebar_nav_legacy_style": True,
    "sidebar_nav_flat_style": True,
    "theme": "darkly",
    "dark_mode_theme": None,
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success",
    },
}

# ------------------------------------------------------------
# CSRF и безопасность
# ------------------------------------------------------------
CSRF_TRUSTED_ORIGINS = [
    "https://dpit-cms.ru",
    "http://dpit-cms.ru",
    "https://www.dpit-cms.ru",
    "http://www.dpit-cms.ru",
    "http://localhost:4234",
    "http://127.0.0.1:4234",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]
CSRF_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SECURE = env.bool('CSRF_COOKIE_SECURE', default=not DEBUG)
SESSION_COOKIE_SECURE = env.bool('SESSION_COOKIE_SECURE', default=not DEBUG)
SECURE_SSL_REDIRECT = env.bool('SECURE_SSL_REDIRECT', default=False)
SECURE_HSTS_SECONDS = env.int('SECURE_HSTS_SECONDS', default=31536000 if not DEBUG and SECURE_SSL_REDIRECT else 0)
SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool('SECURE_HSTS_INCLUDE_SUBDOMAINS', default=not DEBUG and SECURE_SSL_REDIRECT)
SECURE_HSTS_PRELOAD = env.bool('SECURE_HSTS_PRELOAD', default=not DEBUG and SECURE_SSL_REDIRECT)
SECURE_BROWSER_XSS_FILTER = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
X_FRAME_OPTIONS = "DENY"

# ------------------------------------------------------------
# Логирование
# ------------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
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
CACHES = {"default": env.cache('REDIS_URL', default='locmemcache://')}

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
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="admin@dpit-cms.ru")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="V2Jy*qKeb/j?L6")
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
CELERY_BROKER_URL = env("CELERY_BROKER_URL", default="redis://localhost:6379/2")
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
