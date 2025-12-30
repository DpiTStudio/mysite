"""
URL configuration for mysite project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
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
