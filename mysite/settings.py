"""
Настройки Django проекта DPIT-CMS.
Этот файл содержит все основные конфигурации проекта, разделённые на логические секции
для удобства чтения и поддержки. Все комментарии написаны на русском языке.
"""

# ------------------------------------------------------------
# Библиотеки
# ------------------------------------------------------------
import os # Операционная система
from pathlib import Path # Пути к файлам
import importlib.util # Импорт модулей
from celery.schedules import crontab  # Расписание Celery Beat
import environ  # django-environ для чтения .env

# Путь к корню проекта
BASE_DIR = Path(__file__).resolve().parent.parent

# Инициализация django-environ: читаем .env из корня проекта (рядом с manage.py)
env = environ.Env()
environ.Env.read_env(BASE_DIR / ".env")

# ------------------------------------------------------------
# Безопасность
# ------------------------------------------------------------
# Секретный ключ (обязательно в .env, fallback только для тестов)
SECRET_KEY = env.str("SECRET_KEY")
# Режим отладки – НЕ включать в продакшн! (по умолчанию False — безопасно)
DEBUG = env.bool("DEBUG")

# Доступные хосты: базовые всегда включены + дополнительные из .env
domains = ['dpit-cms.ru:4234', 'www.dpit-cms.ru:4234']
hosts = ['127.0.0.1:4234', 'localhost:4234', '46.149.71.34:4234', '192.168.0.4:4234'] + domains

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=hosts)

# ------------------------------------------------------------
# Приложения (INSTALLED_APPS)
# ------------------------------------------------------------
# INSTALLED_APPS = [
#     "jazzmin",
#     # Основные приложения
#     "django.contrib.admin", # Админ панель
#     "django.contrib.auth", # Аутентификация
#     "django.contrib.contenttypes", # Типы контента
#     "django.contrib.sessions", # Сессии
#     "django.contrib.messages", # Сообщения
#     "django.contrib.staticfiles", # Статические файлы
#     "django.contrib.sitemaps",  # Для sitemap.xml
#     "django.contrib.sites",     # Нужно для allauth
#     "captcha",  # Капча
    
#     # Allauth
#     "allauth",
#     "allauth.account",
#     "allauth.socialaccount",
#     "allauth.socialaccount.providers.google",
#     "allauth.socialaccount.providers.github",


#     # Мои приложения
#     "main.apps.MainConfig", # Главная страница
#     "news.apps.NewsConfig", # Новости
#     "portfolio.apps.PortfolioConfig", # Портфолио
#     "reviews.apps.ReviewsConfig", # Отзывы
#     "logfiles.apps.LogfilesConfig", # Логи
#     "accounts.apps.AccountsConfig", # Аккаунты
#     "tickets.apps.TicketsConfig", # Тикеты
#     "mail.apps.MailConfig", # Почта
#     "services.apps.ServicesConfig", # Услуги
#     "cart.apps.CartConfig", # Корзина
#     "favorites.apps.FavoritesConfig", # Избранное
#     "knowledge_base.apps.KnowledgeBaseConfig", # База знаний
#     "tinymce", # Редактор   
# ]
INSTALLED_APPS = [
    # Внешний вид админки (должен быть первым)
    "jazzmin",
    
    # ========== СТАНДАРТНЫЕ ПРИЛОЖЕНИЯ DJANGO ==========
    "django.contrib.admin",           # Админ-панель
    "django.contrib.auth",            # Аутентификация
    "django.contrib.contenttypes",    # Работа с типами моделей
    "django.contrib.sessions",        # Управление сессиями
    "django.contrib.messages",        # Система сообщений
    "django.contrib.staticfiles",     # Статические файлы (CSS, JS)
    "django.contrib.sitemaps",        # Генерация sitemap.xml
    "django.contrib.sites",           # Поддержка нескольких сайтов
    
    # ========== СТОРОННИЕ ПРИЛОЖЕНИЯ ==========
    # Аутентификация через соцсети
    "allauth",                                  # Allauth
    "allauth.account",                          # Allauth account
    "allauth.socialaccount",                    # Allauth social account
    "allauth.socialaccount.providers.google",   # Allauth google
    "allauth.socialaccount.providers.github",   # Allauth github
    
    # Прочие сторонние приложения
    "captcha",        # Защита от ботов
    "tinymce",        # Визуальный редактор
    
    # ========== СОБСТВЕННЫЕ ПРИЛОЖЕНИЯ ==========
    "main.apps.MainConfig",                     # Главная страница
    "accounts.apps.AccountsConfig",             # Управление аккаунтами
    "news.apps.NewsConfig",                     # Новости
    "portfolio.apps.PortfolioConfig",           # Портфолио работ
    "services.apps.ServicesConfig",             # Услуги
    "reviews.apps.ReviewsConfig",               # Отзывы клиентов
    "cart.apps.CartConfig",                     # Корзина покупок
    "favorites.apps.FavoritesConfig",           # Избранное
    "tickets.apps.TicketsConfig",               # Система тикетов (поддержка)
    "knowledge_base.apps.KnowledgeBaseConfig",  # База знаний
    "mail.apps.MailConfig",                     # Почтовые уведомления
    "logfiles.apps.LogfilesConfig",             # Логирование действий
]


# ------------------------------------------------------------
# Middleware
# ------------------------------------------------------------
MIDDLEWARE = [
    # Основные middleware
    "django.middleware.security.SecurityMiddleware",          # Безопасность
    "django.middleware.gzip.GZipMiddleware",                  # Сжатие ответов (Ускорение)
    "django.contrib.sessions.middleware.SessionMiddleware",   # Сессии
    "django.middleware.common.CommonMiddleware",              # Общие настройки
    "django.middleware.csrf.CsrfViewMiddleware",              # CSRF
    "django.contrib.auth.middleware.AuthenticationMiddleware",# Аутентификация
    "django.contrib.messages.middleware.MessageMiddleware",   # Сообщения
    "django.middleware.clickjacking.XFrameOptionsMiddleware", # Защита от кликджекинга
    "allauth.account.middleware.AccountMiddleware",           # Allauth
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
        "APP_DIRS": False, # Приложения (должно быть False, если заданы loaders)
        "OPTIONS": {
            "loaders": [
                (
                    "django.template.loaders.cached.Loader",
                    [
                        "django.template.loaders.filesystem.Loader",
                        "django.template.loaders.app_directories.Loader",
                    ],
                ),
            ] if not DEBUG else [
                "django.template.loaders.filesystem.Loader",
                "django.template.loaders.app_directories.Loader",
            ],
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
    },
}

LANGUAGE_CODE = "ru" # Основной язык
TIME_ZONE = "Europe/Moscow" # Московское время
USE_I18N = True  # Включить интернационализацию
USE_L10N = True  # Включить локализацию
USE_TZ = True # Часовые пояса

LANGUAGES = [
    ('ru', 'Russian'),
]

LOCALE_PATHS = [os.path.join(BASE_DIR, 'locale')]


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
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"}, 
    # Хранилище по умолчанию
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"}, 
    # Хранилище для статических файлов
}
# В продакшене используем манифесты для кеширования
if not DEBUG and HAS_WHITENOISE: # Если DEBUG выключен и WhiteNoise установлен
    # В продакшене используем CompressedManifestStaticFilesStorage без дополнительных опций,
    # чтобы избежать ошибки "unexpected keyword argument 'manifest_strict'".
    STORAGES["staticfiles"] = {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"
    }
# Отключаем строгость манифеста, чтобы сайт не падал при отсутствии файла (ValueError)
WHITENOISE_MANIFEST_STRICT = False
# Кеширование статики на 1 год (для WhiteNoise)
WHITENOISE_MAX_AGE = 31536000 if not DEBUG else 0
WHITENOISE_KEEP_ONLY_HASHED_FILES = True

# ------------------------------------------------------------
# Пользовательская модель и Allauth
# ------------------------------------------------------------
AUTH_USER_MODEL = "accounts.User" # Пользовательская модель
SITE_ID = 1

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

# Настройки Allauth
ACCOUNT_LOGIN_METHODS = {"email"}
ACCOUNT_SIGNUP_FIELDS = ['email*', 'password1*', 'password2*']
ACCOUNT_EMAIL_VERIFICATION = "none" # "mandatory" для продакшена
LOGIN_REDIRECT_URL = "accounts:profile"
LOGOUT_REDIRECT_URL = "main:home"

# Социальные провайдеры (Примеры конфигов)
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': '123_dummy_client_id_for_google',
            'secret': 'dummy_secret_for_google',
            'key': ''
        },
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
        'OAUTH_PKCE_ENABLED': True,
    },
    'github': {
        'APP': {
            'client_id': '123_dummy_client_id_for_github',
            'secret': 'dummy_secret_for_github',
            'key': ''
        },
        'SCOPE': ['user', 'repo', 'read:org'],
    }
}

# ------------------------------------------------------------
# Настройки капчи
# ------------------------------------------------------------
CAPTCHA_CHALLENGE_FUNCT = "captcha.helpers.random_char_challenge" # Функция для генерации капчи
CAPTCHA_LENGTH = 3 
CAPTCHA_TIMEOUT = 5
CAPTCHA_IMAGE_SIZE = (180, 80) # Размеры картинки (ширина, высота)
CAPTCHA_FONT_SIZE = 48 # Размер шрифта на картинке
SECURE_CONTENT_TYPE_NOSNIFF = True

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
    "navigation_expanded": False, # Разворачивать боковую панель
    "hide_apps": [], # Скрывать приложения
    "hide_models": [], # Скрывать модели
    "order_with_respect_to": [
        "auth", # Авторизация
        "main", # Главная
        "knowledge_base", # База знаний
        "news", # Новости
        "portfolio", # Портфолио
        "services", # Услуги
        "reviews", # Отзывы
        "tickets", # Тикеты
        "mail", # Почта
        "cart", # Корзина
        "accounts", # Аккаунты
        "backup", # Бэкапы
        "logfiles", # Логи
    ],
    "custom_links": {
        # Главная
        "main": [{
            "name": "Вернуться на сайт",
            "url": "/",
            "icon": "fas fa-home",
            "new_window": True,
        }, {
            "name": "Аналитика",
            "url": "/admin/dashboard/",
            "icon": "fas fa-chart-line",
            "new_window": False,
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
        "cart.Order": "fas fa-shopping-basket",
        "cart.OrderItem": "fas fa-cart-plus",
        "logfiles.LogFile": "fas fa-file-alt",
        "logfiles.LogBackup": "fas fa-archive",
        "accounts.User": "fas fa-user-circle",
        "admin.LogEntry": "fas fa-history",
    },
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",
    "related_modal_active": False,
    "custom_css": "css/admin_custom.css",
    "custom_js": "js/admin_custom.js",
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
        {"app": "cart", "icon": "fas fa-shopping-cart"},
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
    "footer_fixed": False,
    "sidebar_fixed": True,
    "sidebar": "sidebar-dark-primary",
    "sidebar_nav_small_text": True,
    "sidebar_disable_expand": True,
    "sidebar_nav_child_indent": False,
    "sidebar_nav_compact_style": True,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": True,
    "theme": "darkly",
    "dark_mode_theme": None,
    "button_classes": {
        "primary": "btn-outline-primary",
        "secondary": "btn-outline-secondary",
        "info": "btn-outline-info",
        "warning": "btn-outline-warning",
        "danger": "btn-outline-danger",
        "success": "btn-outline-success"
    },
    "actions_sticky_top": False
}

# JAZZMIN_UI_TWEAKS = {
#     # Настройки внешнего вида
#     "navbar_small_text": True,
#     "footer_small_text": True,
#     "body_small_text": True,
#     "brand_small_text": True,
#     "brand_colour": "navbar-dark",
#     "accent": "accent-primary",
#     "navbar": "navbar-dark",
#     "no_navbar_border": True,
#     "navbar_fixed": False,
#     "layout_boxed": False,
#     "footer_fixed": True,
#     "sidebar_fixed": True,
#     "sidebar": "sidebar-dark-primary",
#     "sidebar_nav_small_text": True,
#     "sidebar_disable_expand": True,
#     "sidebar_nav_child_indent": False,  # Убрать отступы для компактности
#     "sidebar_nav_compact_style": True,
#     "sidebar_nav_legacy_style": False,  # Отключить старый стиль
#     "sidebar_nav_flat_style": True,
#     "theme": "darkly",
#     "dark_mode_theme": None,
#     "button_classes": {
#         "primary": "btn-primary",
#         "secondary": "btn-secondary",
#         "info": "btn-info",
#         "warning": "btn-warning",
#         "danger": "btn-danger",
#         "success": "btn-success",
#     },
# }

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
# Настройки почты (читаются из .env)
# ------------------------------------------------------------
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = env.str("EMAIL_HOST", default="smtp.timeweb.ru")
EMAIL_PORT = env.int("EMAIL_PORT", default=465)
EMAIL_USE_SSL = env.bool("EMAIL_USE_SSL", default=True)
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=False)
EMAIL_HOST_USER = env.str("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env.str("EMAIL_HOST_PASSWORD", default="")
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
SERVER_EMAIL = EMAIL_HOST_USER

# ------------------------------------------------------------
# Настройки IMAP (читаются из .env)
# ------------------------------------------------------------
IMAP_HOST = env.str("IMAP_HOST", default="imap.timeweb.ru")
IMAP_PORT = env.int("IMAP_PORT", default=993)
IMAP_USER = env.str("IMAP_USER", default=EMAIL_HOST_USER)
IMAP_PASSWORD = env.str("IMAP_PASSWORD", default=EMAIL_HOST_PASSWORD)

# ------------------------------------------------------------
# Celery
# ------------------------------------------------------------
CELERY_BROKER_URL = "redis://localhost:6379/2"
CELERY_RESULT_BACKEND = CELERY_BROKER_URL
CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE

# Autodiscover задачи в backup_tasks и других модулях
CELERY_IMPORTS = [
    'mysite.backup_tasks',
]

# Расписание Celery Beat (периодические задачи)
CELERY_BEAT_SCHEDULE = {
    # Полный бэкап (БД + медиа) каждую ночь в 03:00
    'full-backup-nightly': {
        'task': 'backup.full',
        'schedule': crontab(hour=3, minute=0),
        'options': {'expires': 3600},
    },
    # Бэкап только БД каждые 12 часов (в 03:00 и 15:00)
    'db-backup-twice-daily': {
        'task': 'backup.database',
        'schedule': crontab(hour='3,15', minute=0),
        'options': {'expires': 3600},
    },
    # Очистка старых бэкапов каждое воскресенье в 04:00
    'cleanup-old-backups-weekly': {
        'task': 'backup.cleanup',
        'schedule': crontab(hour=4, minute=0, day_of_week=0),
    },
}

# ------------------------------------------------------------
# Настройки резервного копирования
# ------------------------------------------------------------
BACKUP_MAX_DB_COUNT = 14     # Хранить последние 14 бэкапов БД
BACKUP_MAX_MEDIA_COUNT = 7   # Хранить последние 7 архивов медиа

# ------------------------------------------------------------
# Идентификатор корзины в сессии
# ------------------------------------------------------------
CART_SESSION_ID = "cart"

# ------------------------------------------------------------
# Конец файла settings.py
# ------------------------------------------------------------
