from django.db.models import Count, Q
from .models import News, NewsCategory


def latest_news(request):
    """
    Контекстный процессор для добавления последних новостей на все страницы.
    Использует news_date для правильной сортировки по дате события.
    """
    return {
        "latest_news": News.objects.filter(is_active=True)
            .select_related("category")
            .order_by("-news_date", "-created_at")[:3],
        "news_categories": NewsCategory.objects.filter(is_active=True).annotate(
            news_count=Count("news", filter=Q(news__is_active=True))
        ).order_by("order", "name")[:10],
    }
