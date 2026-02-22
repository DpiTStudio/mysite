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
from django.contrib.sitemaps.views import sitemap
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from main import views as main_views
from main.sitemaps import (
    PageSitemap,
    NewsSitemap,
    NewsCategorySitemap,
    PortfolioSitemap,
    PortfolioCategorySitemap,
    StaticViewSitemap,
)

sitemaps = {
    "pages": PageSitemap,
    "news": NewsSitemap,
    "news_categories": NewsCategorySitemap,
    "portfolio": PortfolioSitemap,
    "portfolio_categories": PortfolioCategorySitemap,
    "static": StaticViewSitemap,
}

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("main.urls")),
    path("news/", include("news.urls")),
    path("portfolio/", include("portfolio.urls")),
    path("reviews/", include("reviews.urls")),
    path("accounts/", include("accounts.urls")),
    path("tickets/", include("tickets.urls")),
    path("mail/", include("mail.urls")),
    path("services/", include("services.urls")),
    path("cart/", include("cart.urls")),
    path("knowledge-base/", include("knowledge_base.urls")),
    path("captcha/", include("captcha.urls")),
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
    path("robots.txt", main_views.robots_txt, name="robots"),
    # Игнорировать запросы от Chrome DevToolsExtensions
    path(
        ".well-known/appspecific/com.chrome.devtools.json",
        lambda r: HttpResponse(status=204),
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Обработчики ошибок (работают только когда DEBUG=False)
handler404 = "main.views.page_not_found"
handler500 = "main.views.server_error"
