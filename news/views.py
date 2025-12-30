import logging
from django.shortcuts import render, get_object_or_404
from django.db.models import Count, Avg, Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import Http404
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from .models import News, NewsCategory

logger = logging.getLogger(__name__)


def get_latest_news():
    """Функция для получения последних 3 активных новостей"""
    from django.core.cache import cache
    
    cache_key = "latest_news"
    latest_news = cache.get(cache_key)
    
    if latest_news is None:
        latest_news = list(
            News.objects.filter(is_active=True)
            .select_related("category")
            .order_by("-created_at")[:3]
        )
        cache.set(cache_key, latest_news, 300)  # Кеш на 5 минут
    
    return latest_news


def news_list(request):
    """
    Список всех новостей с пагинацией
    """
    news_queryset = (
        News.objects.filter(is_active=True)
        .select_related("category")
        .order_by("-created_at")
    )
    categories = NewsCategory.objects.filter(is_active=True).annotate(
        news_count=Count("news")
    )

    # Пагинация - 9 новостей на страницу
    paginator = Paginator(news_queryset, 9)
    page = request.GET.get("page")

    try:
        news_list = paginator.page(page)
    except PageNotAnInteger:
        news_list = paginator.page(1)
    except EmptyPage:
        news_list = paginator.page(paginator.num_pages)

    return render(
        request,
        "news/list.html",
        {
            "news_list": news_list,
            "categories": categories,
            "latest_news": get_latest_news(),
        },
    )


def news_by_category(request, category_slug):
    """
    Новости по категории с пагинацией
    """
    category = get_object_or_404(NewsCategory, slug=category_slug, is_active=True)
    news_queryset = (
        News.objects.filter(category=category, is_active=True)
        .select_related("category")
        .order_by("-created_at")
    )

    categories = NewsCategory.objects.filter(is_active=True).annotate(
        news_count=Count("news")
    )

    # Пагинация - 9 новостей на страницу
    paginator = Paginator(news_queryset, 9)
    page = request.GET.get("page")

    try:
        news_list = paginator.page(page)
    except PageNotAnInteger:
        news_list = paginator.page(1)
    except EmptyPage:
        news_list = paginator.page(paginator.num_pages)

    return render(
        request,
        "news/list.html",
        {
            "news_list": news_list,
            "categories": categories,
            "current_category": category,
            "latest_news": get_latest_news(),
        },
    )


def news_search(request):
    """
    Поиск новостей по запросу
    """
    query = request.GET.get("q", "").strip()
    news_queryset = News.objects.none()
    
    if query:
        # Поиск по заголовку, описанию и контенту
        news_queryset = (
            News.objects.filter(is_active=True)
            .filter(
                Q(title__icontains=query)
                | Q(meta_description__icontains=query)
                | Q(content__icontains=query)
            )
            .select_related("category")
            .order_by("-created_at")
        )
    
    categories = NewsCategory.objects.filter(is_active=True).annotate(
        news_count=Count("news")
    )
    
    # Пагинация - 9 новостей на страницу
    paginator = Paginator(news_queryset, 9)
    page = request.GET.get("page")
    
    try:
        news_list = paginator.page(page)
    except PageNotAnInteger:
        news_list = paginator.page(1)
    except EmptyPage:
        news_list = paginator.page(paginator.num_pages)
    
    return render(
        request,
        "news/list.html",
        {
            "news_list": news_list,
            "categories": categories,
            "search_query": query,
            "latest_news": get_latest_news(),
        },
    )


def news_detail(request, slug):
    try:
        news = News.objects.annotate(
            total_comments=Count("comments"), avg_rating=Avg("comments__rating")
        ).get(slug=slug, is_active=True)
    except News.DoesNotExist:
        logger.warning(f"Попытка доступа к несуществующей новости: {slug}")
        raise Http404("Новость не найдена")

    # Увеличиваем счетчик просмотров
    news.increment_views()
    logger.debug(f"Просмотр новости: {news.title} (ID: {news.id}, просмотров: {news.views})")

    context = {
        "news": news,
        "total_comments": news.total_comments,
        "avg_rating": news.avg_rating if news.avg_rating is not None else 0,
    }
    return render(request, "news/detail.html", context)
