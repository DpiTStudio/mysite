from django import template
from django.db.models import Sum
from django.contrib.auth import get_user_model
from news.models import News, NewsCategory
from portfolio.models import Portfolio, PortfolioCategory
from reviews.models import Review
from tickets.models import Ticket
from main.models import Page
from services.models import Service, ServiceOrder
from knowledge_base.models import Article, Category as KBCategory
from cart.models import Order as CartOrder
from logfiles.models import LogFile

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
        'reviews_pending_count': Review.objects.filter(status='pending').count(),
        'tickets_count': Ticket.objects.count(),
        'tickets_open_count': Ticket.objects.exclude(status='closed').count(),
        'pages_count': Page.objects.count(),
        'services_count': Service.objects.count(),
        'service_orders_count': ServiceOrder.objects.count(),
        'service_orders_new_count': ServiceOrder.objects.filter(status='new').count(),
        'total_news_views': News.objects.aggregate(Sum('views'))['views__sum'] or 0,
        'total_portfolio_views': Portfolio.objects.aggregate(Sum('views'))['views__sum'] or 0,
        
        # Новые статистики
        'kb_articles_count': Article.objects.count(),
        'kb_categories_count': KBCategory.objects.count(),
        'cart_orders_count': CartOrder.objects.count(),
        'cart_orders_new_count': CartOrder.objects.filter(status='new').count(),
        'log_files_count': LogFile.objects.count(),
    }
    return stats

@register.filter
def get_model_icon(model_name):
    """
    Возвращает иконку для модели на основе настроек JAZZMIN или стандартную.
    Принимает имя модели (например, 'User' или 'News').
    """
    from django.conf import settings
    
    # Получаем настройки Jazzmin
    jazzmin_settings = getattr(settings, 'JAZZMIN_SETTINGS', {})
    icons = jazzmin_settings.get('icons', {})
    
    icon = "fas fa-circle" # default
    
    # Простой поиск по частичному совпадению имени класса в ключах
    for key, value in icons.items():
        if key.lower().endswith(f".{model_name.lower()}"):
            icon = value
            break
            
    # Специальные переопределения если нужно
    if icon == "fas fa-circle":
        common_icons = {
            'User': 'fas fa-user',
            'Group': 'fas fa-users',
            'SiteSettings': 'fas fa-cogs',
            'Page': 'fas fa-file-alt',
            'News': 'fas fa-newspaper',
            'NewsCategory': 'fas fa-folder',
            'Comment': 'fas fa-comments',
            'Portfolio': 'fas fa-images',
            'PortfolioCategory': 'fas fa-folder-open',
            'Service': 'fas fa-concierge-bell',
            'ServiceOrder': 'fas fa-file-invoice-dollar',
            'Review': 'fas fa-star',
            'Ticket': 'fas fa-ticket-alt',
            'TicketMessage': 'fas fa-comment-dots',
            'Mail': 'fas fa-envelope',
            'LogFile': 'fas fa-file-alt',
            'LogBackup': 'fas fa-archive',
            'LogEntry': 'fas fa-history',
        }
        icon = common_icons.get(model_name, "fas fa-layer-group")
        
    return icon
