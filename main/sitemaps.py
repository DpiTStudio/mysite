from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Page
from news.models import News, NewsCategory
from portfolio.models import Portfolio, PortfolioCategory


class PageSitemap(Sitemap):
    """Sitemap для статических страниц"""
    changefreq = "monthly"
    priority = 0.8

    def items(self):
        return Page.objects.filter(is_active=True)

    def lastmod(self, obj):
        return obj.updated_at


class NewsSitemap(Sitemap):
    """Sitemap для новостей"""
    changefreq = "weekly"
    priority = 0.9

    def items(self):
        return News.objects.filter(is_active=True)

    def lastmod(self, obj):
        return obj.updated_at


class NewsCategorySitemap(Sitemap):
    """Sitemap для категорий новостей"""
    changefreq = "monthly"
    priority = 0.7

    def items(self):
        return NewsCategory.objects.filter(is_active=True)


class PortfolioSitemap(Sitemap):
    """Sitemap для портфолио"""
    changefreq = "monthly"
    priority = 0.8

    def items(self):
        return Portfolio.objects.filter(is_active=True)

    def lastmod(self, obj):
        return obj.updated_at


class PortfolioCategorySitemap(Sitemap):
    """Sitemap для категорий портфолио"""
    changefreq = "monthly"
    priority = 0.7

    def items(self):
        return PortfolioCategory.objects.filter(is_active=True)


class StaticViewSitemap(Sitemap):
    """Sitemap для статических URL"""
    changefreq = "monthly"
    priority = 1.0

    def items(self):
        return ["main:home", "news:list", "portfolio:list", "reviews:list"]

    def location(self, item):
        return reverse(item)

