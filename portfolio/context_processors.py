from .models import Portfolio


def latest_portfolio(request):
    """Контекстный процессор для добавления последних на все страницы"""
    return {
        "latest_portfolio": Portfolio.objects.filter(is_active=True).order_by(
            "-created_at"
        )[:3]
    }
