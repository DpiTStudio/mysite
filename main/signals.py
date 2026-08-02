import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key

# Импортируем модели, которые кэшируются на главной странице
from news.models import News, NewsCategory
from portfolio.models import Portfolio, PortfolioCategory
from services.models import Service, ServiceCategory
from reviews.models import Review
from main.models import Page, SiteSettings

logger = logging.getLogger(__name__)

@receiver([post_save, post_delete], sender=News)
def invalidate_news_cache(sender, instance, **kwargs):
    """Очищает кэш новостей при их изменении"""
    cache.delete("latest_news")
    cache.delete(make_template_fragment_key("homepage_news"))
    logger.info("Кэш новостей очищен.")

@receiver([post_save, post_delete], sender=Portfolio)
def invalidate_portfolio_cache(sender, instance, **kwargs):
    """Очищает кэш портфолио при изменении работ"""
    cache.delete(make_template_fragment_key("homepage_portfolio"))
    logger.info("Кэш портфолио очищен.")

@receiver([post_save, post_delete], sender=Service)
def invalidate_service_cache(sender, instance, **kwargs):
    """Очищает кэш услуг при их изменении"""
    cache.delete(make_template_fragment_key("homepage_services"))
    cache.delete(make_template_fragment_key("site_navigation"))
    logger.info("Кэш услуг очищен.")

@receiver([post_save, post_delete], sender=Review)
def invalidate_review_cache(sender, instance, **kwargs):
    """Очищает кэш отзывов при их изменении"""
    cache.delete(make_template_fragment_key("homepage_reviews"))
    logger.info("Кэш отзывов очищен.")

# Инвалидация кэша навигации (site_navigation)
@receiver([post_save, post_delete], sender=Page)
@receiver([post_save, post_delete], sender=SiteSettings)
@receiver([post_save, post_delete], sender=NewsCategory)
@receiver([post_save, post_delete], sender=PortfolioCategory)
@receiver([post_save, post_delete], sender=ServiceCategory)
def invalidate_navigation_cache(sender, instance, **kwargs):
    """Очищает кэш навигации сайта при изменении категорий или страниц"""
    cache.delete(make_template_fragment_key("site_navigation"))
    logger.info("Кэш навигации очищен.")
