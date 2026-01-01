from django.shortcuts import render, get_object_or_404
from .models import Page
from news.models import News, NewsCategory
from portfolio.models import Portfolio, PortfolioCategory
from reviews.models import Review
from tickets.models import Ticket
from django.contrib.auth import get_user_model
from django.db.models import Sum

User = get_user_model()


def home(request):
    stats = {}
    if request.user.is_staff:
        news_views = News.objects.aggregate(total=Sum("views"))["total"] or 0
        portfolio_views = Portfolio.objects.aggregate(total=Sum("views"))["total"] or 0
        
        stats = {
            "news_count": News.objects.count(),
            "news_categories_count": NewsCategory.objects.count(),
            "portfolio_count": Portfolio.objects.count(),
            "portfolio_categories_count": PortfolioCategory.objects.count(),
            "reviews_count": Review.objects.count(),
            "pending_reviews_count": Review.objects.filter(status="pending").count(),
            "tickets_count": Ticket.objects.count(),
            "open_tickets_count": Ticket.objects.filter(status="open").count(),
            "users_count": User.objects.count(),
            "total_views": news_views + portfolio_views,
        }
    return render(request, "main/home.html", {"stats": stats})


def page_detail(request, slug):
    page = get_object_or_404(Page, slug=slug, is_active=True)
    return render(request, "main/page_detail.html", {"page": page})


def page_not_found(request, exception):
    """Обработчик ошибки 404"""
    return render(request, "404.html", status=404)


def server_error(request):
    """Обработчик ошибки 500"""
    return render(request, "500.html", status=500)


def robots_txt(request):
    """Генерация robots.txt"""
    from django.conf import settings
    scheme = "https" if not settings.DEBUG else "http"
    host = request.get_host()
    return render(
        request,
        "robots.txt",
        {"scheme": scheme, "host": host},
        content_type="text/plain",
    )
