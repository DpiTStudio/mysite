from .models import News


def latest_news(request):
    """Контекстный процессор для добавления последних новостей на все страницы"""
    return {
        "latest_news": News.objects.filter(is_active=True).order_by("-created_at")[:3]
    }
