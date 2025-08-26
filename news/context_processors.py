from .models import News


def latest_news(request):
    """Контекстный процессор для вывода последних новостей на всех страницах"""
    latest_news = News.objects.filter(is_active=True).select_related("category")[:3]
    return {"latest_news": latest_news}
