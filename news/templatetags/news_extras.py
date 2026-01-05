from django import template
from django.db.models import Sum
from django.contrib.auth import get_user_model

register = template.Library()


@register.filter
def sum_news_count(categories):
    """Суммирует количество новостей во всех категориях"""
    return categories.aggregate(total=Sum("news_count"))["total"] or 0


@register.simple_tag
def get_admin_stats():
    from news.models import News, NewsCategory
    from portfolio.models import Portfolio, PortfolioCategory
    from reviews.models import Review
    from tickets.models import Ticket
    from main.models import Page
    from services.models import Service, ServiceOrder
    
    User = get_user_model()
    
    stats = {
        'users_count': User.objects.count(),
        'news_count': News.objects.count(),
        'news_categories_count': NewsCategory.objects.count(),
        'portfolio_count': Portfolio.objects.count(),
        'portfolio_categories_count': PortfolioCategory.objects.count(),
        'services_count': Service.objects.count(),
        'service_orders_count': ServiceOrder.objects.count(),
        'service_orders_new_count': ServiceOrder.objects.filter(status='new').count(),
        'reviews_count': Review.objects.count(),
        'reviews_pending_count': Review.objects.filter(status='pending').count(),
        'tickets_count': Ticket.objects.count(),
        'tickets_open_count': Ticket.objects.exclude(status='closed').count(),
        'pages_count': Page.objects.count(),
        'total_news_views': News.objects.aggregate(Sum('views'))['views__sum'] or 0,
        'total_portfolio_views': Portfolio.objects.aggregate(Sum('views'))['views__sum'] or 0,
    }
    return stats
