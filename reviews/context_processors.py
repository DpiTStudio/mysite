from .models import Review


def latest_reviews(request):
    """Контекстный процессор для добавления последних отзывов на все страницы"""
    return {
        "latest_reviews": Review.objects.filter(status="approved").order_by("-created_at")[:3]
    }
