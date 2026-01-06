"""
Модуль sitemaps.py приложения main

Этот файл содержит классы для генерации XML-карты сайта (sitemap.xml).
Sitemap помогает поисковым системам (Google, Yandex и др.) находить и индексировать
все страницы сайта.

Каждый класс Sitemap определяет:
- Какие объекты включать в карту сайта (метод items)
- Частоту обновления страниц (changefreq)
- Приоритет страниц для поисковиков (priority)
- Дату последнего изменения (lastmod, опционально)
"""

# Импорт базового класса Sitemap из Django
from django.contrib.sitemaps import Sitemap
# Импорт функции reverse для преобразования имен маршрутов в URL
from django.urls import reverse
# Импорт моделей приложения main
from .models import Page
# Импорт моделей из других приложений
from news.models import News, NewsCategory
from portfolio.models import Portfolio, PortfolioCategory


class PageSitemap(Sitemap):
    """
    Sitemap для статических страниц сайта.
    
    Включает все активные страницы из модели Page.
    Используется для индексации страниц типа "О нас", "Контакты" и т.д.
    """
    # Частота обновления страниц (monthly = раз в месяц)
    # Указывает поисковым системам, как часто обновляется контент
    changefreq = "monthly"
    
    # Приоритет страницы (0.0 - 1.0)
    # 0.8 - высокий приоритет (статические страницы важны для сайта)
    priority = 0.8

    def items(self):
        """
        Возвращает список объектов для включения в sitemap.
        
        Returns:
            QuerySet: Список активных страниц из базы данных
        """
        return Page.objects.filter(is_active=True)

    def lastmod(self, obj):
        """
        Возвращает дату последнего изменения объекта.
        
        Args:
            obj: Экземпляр модели Page
        
        Returns:
            datetime: Дата последнего обновления страницы
        """
        return obj.updated_at


class NewsSitemap(Sitemap):
    """
    Sitemap для новостей сайта.
    
    Включает все активные новости для индексации поисковыми системами.
    Новости обновляются чаще, чем статические страницы, поэтому changefreq = "weekly".
    """
    # Новости обновляются еженедельно
    changefreq = "weekly"
    
    # Высокий приоритет (0.9) - новости важны для SEO
    priority = 0.9

    def items(self):
        """
        Возвращает список активных новостей.
        
        Returns:
            QuerySet: Список активных новостей
        """
        return News.objects.filter(is_active=True)

    def lastmod(self, obj):
        """
        Возвращает дату последнего изменения новости.
        
        Args:
            obj: Экземпляр модели News
        
        Returns:
            datetime: Дата последнего обновления новости
        """
        return obj.updated_at


class NewsCategorySitemap(Sitemap):
    """
    Sitemap для категорий новостей.
    
    Включает страницы категорий новостей для индексации.
    Категории обновляются реже, чем сами новости.
    """
    # Категории обновляются раз в месяц
    changefreq = "monthly"
    
    # Средний приоритет (0.7) - категории важны, но не критичны
    priority = 0.7

    def items(self):
        """
        Возвращает список активных категорий новостей.
        
        Returns:
            QuerySet: Список активных категорий новостей
        """
        return NewsCategory.objects.filter(is_active=True)


class PortfolioSitemap(Sitemap):
    """
    Sitemap для работ портфолио.
    
    Включает все активные работы портфолио для индексации.
    Портфолио обновляется реже, чем новости.
    """
    # Портфолио обновляется раз в месяц
    changefreq = "monthly"
    
    # Высокий приоритет (0.8) - портфолио важно для демонстрации работ
    priority = 0.8

    def items(self):
        """
        Возвращает список активных работ портфолио.
        
        Returns:
            QuerySet: Список активных работ портфолио
        """
        return Portfolio.objects.filter(is_active=True)

    def lastmod(self, obj):
        """
        Возвращает дату последнего изменения работы.
        
        Args:
            obj: Экземпляр модели Portfolio
        
        Returns:
            datetime: Дата последнего обновления работы
        """
        return obj.updated_at


class PortfolioCategorySitemap(Sitemap):
    """
    Sitemap для категорий портфолио.
    
    Включает страницы категорий портфолио для индексации.
    """
    # Категории обновляются раз в месяц
    changefreq = "monthly"
    
    # Средний приоритет (0.7)
    priority = 0.7

    def items(self):
        """
        Возвращает список активных категорий портфолио.
        
        Returns:
            QuerySet: Список активных категорий портфолио
        """
        return PortfolioCategory.objects.filter(is_active=True)


class StaticViewSitemap(Sitemap):
    """
    Sitemap для статических URL (представлений без модели).
    
    Включает главные страницы разделов сайта, которые не привязаны к моделям:
    - Главная страница
    - Список новостей
    - Список портфолио
    - Список отзывов
    """
    # Статические страницы обновляются раз в месяц
    changefreq = "monthly"
    
    # Максимальный приоритет (1.0) - главные страницы самые важные
    priority = 1.0

    def items(self):
        """
        Возвращает список имен маршрутов для включения в sitemap.
        
        Returns:
            list: Список строк с именами маршрутов
        """
        return ["main:home", "news:list", "portfolio:list", "reviews:list"]

    def location(self, item):
        """
        Преобразует имя маршрута в полный URL.
        
        Args:
            item (str): Имя маршрута (например, "main:home")
        
        Returns:
            str: Полный URL (например, "/")
        """
        return reverse(item)

