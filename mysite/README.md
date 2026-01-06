# Основные настройки проекта DPIT-CMS

## Описание

Директория `mysite` содержит основные настройки Django проекта DPIT-CMS. Это корневая директория конфигурации, которая включает настройки приложения, URL-маршрутизацию, WSGI/ASGI конфигурацию и другие глобальные параметры.

---

## Структура файлов

### `settings.py` - Основные настройки проекта

Файл содержит все настройки Django проекта.

#### Секретные ключи и безопасность

```python
SECRET_KEY = os.environ.get("SECRET_KEY", "fallback-ключ")
DEBUG = os.environ.get("DEBUG", "True").lower() in ("true", "1", "yes")
ALLOWED_HOSTS = ["*", "dpit-cms.ru", "213.171.7.204", "localhost", "127.0.0.1"]
```

**Описание:**
- `SECRET_KEY` - Используется для криптографической подписи. Рекомендуется хранить в переменных окружения.
- `DEBUG` - Режим отладки. Должен быть `False` в production!
- `ALLOWED_HOSTS` - Список разрешенных доменов/IP для работы сайта.

#### Установленные приложения (INSTALLED_APPS)

```python
INSTALLED_APPS = [
    "jazzmin",           # Админ-панель с улучшенным UI
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",  # Для sitemap.xml
    "captcha",           # Капча для форм
    "main",              # Основное приложение
    "news",              # Новости
    "portfolio",         # Портфолио и услуги
    "reviews",           # Отзывы
    "logfiles",          # Управление логами
    "accounts",          # Пользователи и авторизация
    "tickets",           # Система тикетов
    "mail",              # Управление почтой
    "services",          # Услуги
    "tinymce",           # HTML-редактор
]
```

**Описание приложений:**
- `jazzmin` - Кастомизированная админ-панель Django
- `captcha` - Защита форм от спама
- `main` - Основное приложение (страницы, настройки сайта)
- `news` - Система новостей
- `portfolio` - Портфолио работ и услуги
- `reviews` - Система отзывов
- `logfiles` - Управление файлами логов
- `accounts` - Расширенная модель пользователя и авторизация
- `tickets` - Система тикетов поддержки
- `mail` - Управление электронной почтой
- `services` - Расширенная система услуг
- `tinymce` - WYSIWYG HTML-редактор

#### Middleware

```python
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
```

**Описание:**
- Обработка безопасности, сессий, CSRF-защиты, авторизации, сообщений и защиты от clickjacking.

#### База данных

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
```

**Текущая конфигурация:**
- Используется SQLite для разработки
- Для production рекомендуется PostgreSQL или MySQL

#### Модель пользователя

```python
AUTH_USER_MODEL = "accounts.User"
```

**Описание:**
- Используется кастомная модель пользователя из приложения `accounts`.

#### Статические и медиа файлы

```python
STATIC_URL = "/static/"
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
```

**Описание:**
- `STATIC_URL` - URL для статических файлов (CSS, JS, изображения)
- `STATICFILES_DIRS` - Директории со статическими файлами в разработке
- `STATIC_ROOT` - Директория для сбора статических файлов при деплое
- `MEDIA_URL` - URL для загруженных пользователями файлов
- `MEDIA_ROOT` - Директория для хранения медиа-файлов

#### Локализация

```python
LANGUAGE_CODE = "ru-ru"
TIME_ZONE = "Europe/Moscow"
USE_I18N = True
USE_TZ = True
```

**Описание:**
- Русский язык и московский часовой пояс.

#### Настройки Jazzmin (Админ-панель)

```python
JAZZMIN_SETTINGS = {
    "site_title": "DPIT-CMS Admin",
    "site_header": "DPIT-CMS",
    "site_brand": "DPIT-CMS",
    "welcome_sign": "Добро пожаловать в админ-панель DPIT-CMS",
    "show_ui_builder": True,
    "changeform_format": "horizontal_tabs",
    # ... другие настройки
}
```

**Описание:**
- Кастомизация внешнего вида и функциональности админ-панели.
- Настройка меню, иконок, структуры.

#### Настройки CSRF

```python
CSRF_TRUSTED_ORIGINS = [
    "https://dpit-cms.ru",
    "http://dpit-cms.ru",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]
```

**Описание:**
- Доверенные источники для CSRF-токенов.

#### Настройки TinyMCE (HTML-редактор)

```python
TINYMCE_DEFAULT_CONFIG = {
    "height": 360,
    "width": "100%",
    "language": "ru",
    "plugins": "advlist autolink lists link image charmap print preview anchor",
    "toolbar": "undo redo | styleselect | bold italic | alignleft aligncenter alignright alignjustify | bullist numlist outdent indent | link image",
    # ... другие настройки
}
```

**Описание:**
- Конфигурация WYSIWYG редактора для HTML-контента.

#### Настройки безопасности (для production)

```python
CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
SECURE_SSL_REDIRECT = not DEBUG
SECURE_HSTS_SECONDS = 31536000 if not DEBUG else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = not DEBUG
SECURE_HSTS_PRELOAD = not DEBUG
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = "DENY"
```

**Описание:**
- Настройки безопасности для HTTPS в production.

#### Настройки логирования

```python
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": BASE_DIR / "logs" / "django.log",
        },
        "console": {
            "level": "DEBUG" if DEBUG else "INFO",
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console", "file"],
            "level": "INFO",
        },
        "news": {
            "handlers": ["console", "file"],
            "level": "DEBUG" if DEBUG else "INFO",
        },
    },
}
```

**Описание:**
- Логирование в файл и консоль.
- Разные уровни для разработки и production.

#### Кеширование

```python
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "unique-snowflake",
        "TIMEOUT": 300,  # 5 минут
        "OPTIONS": {
            "MAX_ENTRIES": 1000,
        },
    }
}
```

**Описание:**
- In-memory кеш для оптимизации производительности.

#### Настройки почты (SMTP)

```python
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.timeweb.ru"
EMAIL_PORT = 465
EMAIL_USE_SSL = True
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "admin@dpit-cms.ru")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "пароль")
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
SERVER_EMAIL = EMAIL_HOST_USER
```

**Описание:**
- Настройки для отправки email через SMTP (Timeweb).

#### Настройки IMAP

```python
IMAP_HOST = "imap.timeweb.ru"
IMAP_PORT = 993
IMAP_USER = EMAIL_HOST_USER
IMAP_PASSWORD = EMAIL_HOST_PASSWORD
```

**Описание:**
- Настройки для чтения входящих писем через IMAP (Timeweb).

---

### `urls.py` - Основная конфигурация URL

Файл определяет корневые URL-маршруты проекта.

**Основные маршруты:**

```python
urlpatterns = [
    path("admin/", admin.site.urls),           # Админ-панель
    path("", include("main.urls")),            # Главная страница и основные страницы
    path("news/", include("news.urls")),       # Новости
    path("portfolio/", include("portfolio.urls")),  # Портфолио
    path("reviews/", include("reviews.urls")), # Отзывы
    path("accounts/", include("accounts.urls")),  # Авторизация
    path("tickets/", include("tickets.urls")), # Тикеты
    path("mail/", include("mail.urls")),       # Почта
    path("services/", include("services.urls")),  # Услуги
    path("captcha/", include("captcha.urls")), # Капча
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}),  # Sitemap
    path("robots.txt", main_views.robots_txt),  # Robots.txt
]
```

**Sitemap конфигурация:**

```python
sitemaps = {
    "pages": PageSitemap,
    "news": NewsSitemap,
    "news_categories": NewsCategorySitemap,
    "portfolio": PortfolioSitemap,
    "portfolio_categories": PortfolioCategorySitemap,
    "static": StaticViewSitemap,
}
```

**Обработчики ошибок:**

```python
handler404 = "main.views.page_not_found"
handler500 = "main.views.server_error"
```

**Описание:**
- Объединяет все URL-маршруты приложений.
- Настраивает sitemap для SEO.
- Обрабатывает ошибки 404 и 500.

---

### `wsgi.py` - WSGI конфигурация

Файл для развертывания приложения через WSGI (например, для Apache или Nginx с Gunicorn).

**Содержимое:**
- Экспортирует объект `application` для WSGI-сервера
- Устанавливает `DJANGO_SETTINGS_MODULE` на `mysite.settings`

**Использование:**
```bash
gunicorn mysite.wsgi:application
```

---

### `asgi.py` - ASGI конфигурация

Файл для развертывания приложения через ASGI (для асинхронных серверов, WebSockets).

**Содержимое:**
- Аналогично `wsgi.py`, но для ASGI-серверов

**Использование:**
```bash
uvicorn mysite.asgi:application
```

---

### `__init__.py` - Инициализация пакета

Пустой файл, делает директорию Python-пакетом.

---

## Контекстные процессоры

Настроены в `settings.py`:

```python
TEMPLATES = [
    {
        "OPTIONS": {
            "context_processors": [
                "main.context_processors.main_context",
                "news.context_processors.latest_news",
                "portfolio.context_processors.latest_portfolio",
                "reviews.context_processors.latest_reviews",
            ],
        },
    },
]
```

**Описание:**
- Автоматически добавляют данные в контекст всех шаблонов:
  - Основной контекст (настройки сайта)
  - Последние новости
  - Последние работы портфолио
  - Последние отзывы

---

## Переменные окружения

Рекомендуется использовать следующие переменные окружения:

- `SECRET_KEY` - Секретный ключ Django
- `DEBUG` - Режим отладки (True/False)
- `EMAIL_HOST_USER` - Email для отправки писем
- `EMAIL_HOST_PASSWORD` - Пароль для email

**Установка в Linux/Mac:**
```bash
export SECRET_KEY="ваш-секретный-ключ"
export DEBUG="False"
```

**Установка в Windows:**
```cmd
set SECRET_KEY=ваш-секретный-ключ
set DEBUG=False
```

---

## Развертывание

### Для разработки

```bash
python manage.py runserver
```

### Для production

1. Установите `DEBUG = False` в `settings.py`
2. Настройте `ALLOWED_HOSTS`
3. Соберите статические файлы:
   ```bash
   python manage.py collectstatic
   ```
4. Настройте веб-сервер (Nginx/Apache) для статических файлов
5. Запустите через WSGI/ASGI сервер:
   ```bash
   gunicorn mysite.wsgi:application
   ```

---

## Безопасность

### Рекомендации для production

1. **Никогда не коммитьте `SECRET_KEY` в репозиторий**
   - Используйте переменные окружения

2. **Установите `DEBUG = False`**
   - Отключите режим отладки в production

3. **Настройте `ALLOWED_HOSTS`**
   - Укажите только ваши домены

4. **Используйте HTTPS**
   - Настройки безопасности включены в `settings.py`

5. **Используйте безопасную базу данных**
   - PostgreSQL или MySQL вместо SQLite

6. **Регулярно обновляйте зависимости**
   - Проверяйте уязвимости

---

## Зависимости

Основные зависимости проекта:

- Django 4.2.7+
- django-jazzmin (админ-панель)
- django-captcha (капча)
- django-tinymce (HTML-редактор)

Полный список зависимостей в `requirements.txt`.

---

## Структура проекта

```
mysite/
├── mysite/          # Основные настройки (эта директория)
│   ├── settings.py  # Настройки проекта
│   ├── urls.py      # URL-маршрутизация
│   ├── wsgi.py      # WSGI конфигурация
│   └── asgi.py      # ASGI конфигурация
├── main/            # Основное приложение
├── news/            # Новости
├── portfolio/       # Портфолио
├── reviews/         # Отзывы
├── logfiles/        # Логи
├── accounts/        # Пользователи
├── tickets/         # Тикеты
├── mail/            # Почта
├── services/        # Услуги
├── templates/       # Шаблоны
├── static/          # Статические файлы
└── media/           # Медиа-файлы
```

---

## Дополнительные настройки

### Логи

Директория `logs/` автоматически создается при первом запуске. Логи сохраняются в `logs/django.log`.

### Медиа-файлы

Все загруженные пользователями файлы сохраняются в директории `media/`:
- `media/news/` - Изображения новостей
- `media/portfolio/` - Работы портфолио
- `media/services/` - Иконки услуг
- И т.д.

### Статические файлы

Статические файлы собираются в `staticfiles/` при выполнении `collectstatic`.

---

## Поддержка

Для получения помощи по настройке и использованию проекта обращайтесь к документации каждого приложения в соответствующих README.md файлах.
