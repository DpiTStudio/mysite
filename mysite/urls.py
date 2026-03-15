"""
Конфигурация URL для проекта mysite.

Список `urlpatterns` направляет URL-адреса в представления (views). Дополнительную информацию можно найти здесь:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Примеры:
Представления на основе функций
    1. Добавьте импорт:  from my_app import views
    2. Добавьте URL в urlpatterns:  path('', views.home, name='home')
Представления на основе классов
    1. Добавьте импорт:  from other_app.views import Home
    2. Добавьте URL в urlpatterns:  path('', Home.as_view(), name='home')
Интеграция других конфигураций URL
    1. Импортируйте функцию include(): from django.urls import include, path
    2. Добавьте URL в urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin 
# Админ-панель
from django.contrib.sitemaps.views import sitemap 
# Карта сайта
from django.urls import path, include 
# Пути и включение других конфигураций URL
from django.conf import settings 
# Настройки проекта
from django.conf.urls.static import static 
# Статические файлы
from django.http import HttpResponse 
# HTTP-ответы
from django.views.static import serve 
# Сервер статических файлов
from django.views.generic import RedirectView 
# Перенаправление
from main import views as main_views 
# Главная страница
from main.sitemaps import (
    PageSitemap, 
    # Карта сайта
    NewsSitemap, 
    # Новости
    NewsCategorySitemap, 
    # Категории новостей
    PortfolioSitemap, 
    # Портфолио
    PortfolioCategorySitemap, 
    # Категории портфолио
    StaticViewSitemap, 
    # Статические страницы
)

sitemaps = {
    "pages": PageSitemap, 
    # Карта сайта
    "news": NewsSitemap, 
    # Новости
    "news_categories": NewsCategorySitemap, 
    # Категории новостей
    "portfolio": PortfolioSitemap, 
    # Портфолио
    "portfolio_categories": PortfolioCategorySitemap, 
    # Категории портфолио
    "static": StaticViewSitemap, 
    # Статические страницы
}
urlpatterns = [
    path('media/<path:path>', serve, {'document_root': settings.MEDIA_ROOT}), 
    # Медиа файлы
    path('static/<path:path>', serve, {'document_root': settings.STATIC_ROOT}), 
    # Статические файлы
    path("admin/dashboard/", main_views.admin_dashboard, name="admin_dashboard"), 
    # Админ-панель
    path('favicon.ico', RedirectView.as_view(url=settings.STATIC_URL + 'images/favicon.ico')), 
    # Фавикон
    path(
        ".well-known/appspecific/com.chrome.devtools.json", 
        # Google DevTools
        lambda r: HttpResponse(status=204),
    ),
    path(
        "sitemap.xml", 
        # Карта сайта
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
    path("robots.txt", main_views.robots_txt, name="robots"), # Роботс.тхт
]

urlpatterns += [
    path("", include("main.urls")), 
    # Главная страница
    path("admin/", admin.site.urls), 
    # Админ-панель
    path("news/", include("news.urls")), 
    # Новости
    path("portfolio/", include("portfolio.urls")), 
    # Портфолио
    path("reviews/", include("reviews.urls")), 
    # Отзывы
    path("accounts/", include("accounts.urls")), 
    # Аккаунты
    path("accounts/", include("allauth.urls")), 
    # Социальный логин
    path("tickets/", include("tickets.urls")), 
    # Тикеты
    path("mail/", include("mail.urls")), 
    # Почта
    path("services/", include("services.urls")), 
    # Услуги
    path("cart/", include("cart.urls")), 
    # Корзина
    path("favorites/", include("favorites.urls")), 
    # Избранное
    path("knowledge-base/", include("knowledge_base.urls")), 
    # База знаний
    path("captcha/", include("captcha.urls")), 
    # Капча
]

# Обработчики ошибок (работают только когда DEBUG=False)
handler404 = "main.views.page_not_found" 
# Обработчик ошибок 404
handler500 = "main.views.server_error" 
# Обработчик ошибок 500

if settings.DEBUG:
    # В режиме отладки также используем стандартные хелперы для статики
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 
    # Медиа файлы
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) 
    # Статические файлы
