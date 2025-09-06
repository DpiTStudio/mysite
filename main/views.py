from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.core.cache import cache
from django.http import Http404
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView
from django.db.models import Q
from .models import Page, SiteSettings


def get_site_settings():
    """Получает настройки сайта с кэшированием"""
    settings = cache.get('site_settings')
    if not settings:
        settings = SiteSettings.objects.filter(is_active=True).first()
        if settings:
            cache.set('site_settings', settings, 3600)  # Кэш на 1 час
    return settings


@cache_page(60 * 15)  # Кэш на 15 минут
@vary_on_headers('Accept-Language')
def home(request):
    """Главная страница"""
    try:
        site_settings = get_site_settings()
        context = {
            'site_settings': site_settings,
            'pages': Page.objects.filter(
                is_active=True, 
                show_in_menu=True, 
                parent__isnull=True
            ).order_by('order', 'title')[:10]
        }
        return render(request, "main/home.html", context)
    except Exception as e:
        # Логирование ошибки
        print(f"Ошибка на главной странице: {e}")
        return render(request, "main/home.html", {
            'error': 'Произошла ошибка при загрузке страницы'
        })


@cache_page(60 * 30)  # Кэш на 30 минут
@vary_on_headers('Accept-Language')
def page_detail(request, slug):
    """Детальная страница"""
    try:
        page = get_object_or_404(
            Page.objects.select_related('parent'), 
            slug=slug, 
            is_active=True
        )
        
        # Получаем настройки сайта
        site_settings = get_site_settings()
        
        # Получаем хлебные крошки
        breadcrumbs = page.get_breadcrumbs()
        
        # Получаем дочерние страницы
        children = page.children.filter(is_active=True).order_by('order', 'title')
        
        # Получаем соседние страницы
        siblings = Page.objects.filter(
            parent=page.parent,
            is_active=True
        ).exclude(pk=page.pk).order_by('order', 'title')
        
        context = {
            'page': page,
            'site_settings': site_settings,
            'breadcrumbs': breadcrumbs,
            'children': children,
            'siblings': siblings,
        }
        
        # Используем шаблон из модели, если указан
        template = page.template or "main/page_detail.html"
        return render(request, template, context)
        
    except Http404:
        raise
    except Exception as e:
        print(f"Ошибка на странице {slug}: {e}")
        raise Http404("Страница не найдена")


class PageListView(ListView):
    """Список страниц"""
    model = Page
    template_name = 'main/page_list.html'
    context_object_name = 'pages'
    paginate_by = 20
    
    def get_queryset(self):
        """Фильтруем только активные страницы"""
        return Page.objects.filter(is_active=True).order_by('order', 'title')
    
    def get_context_data(self, **kwargs):
        """Добавляем дополнительные данные в контекст"""
        context = super().get_context_data(**kwargs)
        context['site_settings'] = get_site_settings()
        return context


def search_pages(request):
    """Поиск по страницам"""
    query = request.GET.get('q', '').strip()
    pages = []
    
    if query:
        pages = Page.objects.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(meta_keywords__icontains=query),
            is_active=True
        ).order_by('order', 'title')
    
    # Пагинация
    paginator = Paginator(pages, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'query': query,
        'pages': page_obj,
        'site_settings': get_site_settings(),
    }
    
    return render(request, 'main/search.html', context)


def sitemap(request):
    """Карта сайта"""
    try:
        pages = Page.objects.filter(is_active=True).order_by('order', 'title')
        site_settings = get_site_settings()
        
        context = {
            'pages': pages,
            'site_settings': site_settings,
        }
        
        return render(request, 'main/sitemap.html', context)
    except Exception as e:
        print(f"Ошибка при создании карты сайта: {e}")
        return render(request, 'main/sitemap.html', {'pages': []})
