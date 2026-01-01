from django import template
from django.db.models import Sum
from django.contrib.auth import get_user_model
from news.models import News, NewsCategory
from portfolio.models import Portfolio, PortfolioCategory
from reviews.models import Review
from tickets.models import Ticket
from main.models import Page

register = template.Library()
User = get_user_model()

@register.simple_tag
def get_admin_stats():
    stats = {
        'users_count': User.objects.count(),
        'news_count': News.objects.count(),
        'news_categories_count': NewsCategory.objects.count(),
        'portfolio_count': Portfolio.objects.count(),
        'portfolio_categories_count': PortfolioCategory.objects.count(),
        'reviews_count': Review.objects.count(),
        'reviews_pending_count': Review.objects.filter(is_active=False).count(),
        'tickets_count': Ticket.objects.count(),
        'tickets_open_count': Ticket.objects.exclude(status='closed').count(),
        'pages_count': Page.objects.count(),
        'total_news_views': News.objects.aggregate(Sum('views'))['views__sum'] or 0,
        'total_portfolio_views': Portfolio.objects.aggregate(Sum('views'))['views__sum'] or 0,
    }
    return stats
