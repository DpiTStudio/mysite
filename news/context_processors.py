from django.db.models import Count
from .models import News, NewsCategory


def latest_news(request):
    """Контекстный процессор для добавления последних новостей на все страницы"""
    return {
        "latest_news": News.objects.filter(is_active=True).order_by("-created_at")[:3],
        "categories": NewsCategory.objects.filter(is_active=True).annotate(
            news_count=Count("news")
        )[:10],  # Ограничиваем для производительности
    }
