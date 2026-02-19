import logging
from django.shortcuts import render, get_object_or_404
from django.db.models import Count, Avg, Q, Prefetch
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import Http404
from .models import News, NewsCategory, DailyEvent
from collections import OrderedDict

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
            .order_by("-news_date", "-created_at")[:3]
        )
        cache.set(cache_key, latest_news, 300)  # Кеш на 5 минут
    
    return latest_news


def _group_news_by_date(news_page):
    """
    Группирует новости по дате (news_date).
    Все новости добавленные/обновлённые в один день группируются вместе,
    независимо от категории.
    
    Returns:
        OrderedDict: Словарь {date: [news1, news2, ...]}
    """
    grouped = OrderedDict()
    for item in news_page:
        date_key = item.news_date
        if date_key not in grouped:
            grouped[date_key] = []
        grouped[date_key].append(item)
    return grouped


def _get_sort_param(request):
    """Получает параметр сортировки из запроса"""
    sort = request.GET.get("sort", "date_desc")
    sort_options = {
        "date_desc": "-news_date",
        "date_asc": "news_date",
        "views_desc": "-views",
        "views_asc": "views",
        "title_asc": "title",
        "title_desc": "-title",
    }
    return sort_options.get(sort, "-news_date"), sort


def news_list(request):
    """
    Отображает список всех активных новостей с пагинацией.
    Поддерживает группировку по дате и сортировку.
    """
    order_field, current_sort = _get_sort_param(request)
    
    news_queryset = (
        News.objects.filter(is_active=True)
        .select_related("category")
        .prefetch_related(
            Prefetch("events", queryset=DailyEvent.objects.order_by("order", "-created_at"))
        )
        .annotate(events_count=Count("events"))
        .order_by(order_field, "-created_at")
    )
    categories = NewsCategory.objects.filter(is_active=True).annotate(
        news_count=Count("news", filter=Q(news__is_active=True))
    )

    # Пагинация - 12 новостей на страницу
    paginator = Paginator(news_queryset, 12)
    page = request.GET.get("page")

    try:
        news_list = paginator.page(page)
    except PageNotAnInteger:
        news_list = paginator.page(1)
    except EmptyPage:
        news_list = paginator.page(paginator.num_pages)

    # Группируем по дате
    grouped_news = _group_news_by_date(news_list)

    return render(
        request,
        "news/list.html",
        {
            "news_list": news_list,
            "grouped_news": grouped_news,
            "categories": categories,
            "latest_news": get_latest_news(),
            "current_sort": current_sort,
        },
    )


def news_by_category(request, category_slug):
    """
    Отображает новости, отфильтрованные по определенной категории.
    """
    category = get_object_or_404(NewsCategory, slug=category_slug, is_active=True)
    order_field, current_sort = _get_sort_param(request)
    
    news_queryset = (
        News.objects.filter(category=category, is_active=True)
        .select_related("category")
        .prefetch_related(
            Prefetch("events", queryset=DailyEvent.objects.order_by("order", "-created_at"))
        )
        .annotate(events_count=Count("events"))
        .order_by(order_field, "-created_at")
    )

    categories = NewsCategory.objects.filter(is_active=True).annotate(
        news_count=Count("news", filter=Q(news__is_active=True))
    )

    # Пагинация - 12 новостей на страницу
    paginator = Paginator(news_queryset, 12)
    page = request.GET.get("page")

    try:
        news_list = paginator.page(page)
    except PageNotAnInteger:
        news_list = paginator.page(1)
    except EmptyPage:
        news_list = paginator.page(paginator.num_pages)

    # Группируем по дате
    grouped_news = _group_news_by_date(news_list)

    return render(
        request,
        "news/list.html",
        {
            "news_list": news_list,
            "grouped_news": grouped_news,
            "categories": categories,
            "current_category": category,
            "latest_news": get_latest_news(),
            "current_sort": current_sort,
        },
    )


def news_by_date(request, year, month, day):
    """
    Отображает все новости за конкретную дату (все категории).
    Позволяет увидеть все события, произошедшие в один день.
    """
    from datetime import date
    
    try:
        target_date = date(year, month, day)
    except ValueError:
        raise Http404("Некорректная дата")
    
    news_queryset = (
        News.objects.filter(is_active=True, news_date=target_date)
        .select_related("category")
        .prefetch_related(
            Prefetch("events", queryset=DailyEvent.objects.order_by("order", "-created_at"))
        )
        .annotate(events_count=Count("events"))
        .order_by("category__name", "-created_at")
    )

    categories = NewsCategory.objects.filter(is_active=True).annotate(
        news_count=Count("news", filter=Q(news__is_active=True))
    )

    return render(
        request,
        "news/list.html",
        {
            "news_list": news_queryset,
            "grouped_news": {target_date: list(news_queryset)},
            "categories": categories,
            "target_date": target_date,
            "latest_news": get_latest_news(),
            "current_sort": "date_desc",
        },
    )


def news_search(request):
    """
    Выполняет поиск новостей по текстовому запросу.
    """
    query = request.GET.get("q", "").strip()
    news_queryset = News.objects.none()
    
    if query:
        # Поиск по заголовку, описанию, контенту и категории
        news_queryset = (
            News.objects.filter(is_active=True)
            .filter(
                Q(title__icontains=query)
                | Q(meta_description__icontains=query)
                | Q(content__icontains=query)
                | Q(category__name__icontains=query)
            )
            .select_related("category")
            .prefetch_related(
                Prefetch("events", queryset=DailyEvent.objects.order_by("order", "-created_at"))
            )
            .annotate(events_count=Count("events"))
            .order_by("-news_date", "-created_at")
        )
    
    categories = NewsCategory.objects.filter(is_active=True).annotate(
        news_count=Count("news", filter=Q(news__is_active=True))
    )
    
    # Пагинация - 12 новостей на страницу
    paginator = Paginator(news_queryset, 12)
    page = request.GET.get("page")
    
    try:
        news_list = paginator.page(page)
    except PageNotAnInteger:
        news_list = paginator.page(1)
    except EmptyPage:
        news_list = paginator.page(paginator.num_pages)
    
    # Группируем по дате
    grouped_news = _group_news_by_date(news_list)
    
    return render(
        request,
        "news/list.html",
        {
            "news_list": news_list,
            "grouped_news": grouped_news,
            "categories": categories,
            "search_query": query,
            "latest_news": get_latest_news(),
            "current_sort": "date_desc",
        },
    )


def news_detail(request, slug):
    """
    Отображает детальную страницу конкретной новости.
    Включает события дня и связанные новости.
    """
    try:
        news = (
            News.objects
            .select_related("category")
            .prefetch_related(
                Prefetch("events", queryset=DailyEvent.objects.order_by("order", "-created_at")),
                "comments",
            )
            .annotate(
                total_comments=Count("comments"), 
                avg_rating=Avg("comments__rating"),
                events_count=Count("events"),
            )
            .get(slug=slug, is_active=True)
        )
    except News.DoesNotExist:
        logger.warning(f"Попытка доступа к несуществующей новости: {slug}")
        raise Http404("Новость не найдена")

    # Увеличиваем счетчик просмотров
    news.increment_views()
    logger.debug(f"Просмотр новости: {news.title} (ID: {news.id}, просмотров: {news.views})")

    # Получаем события дня
    events = news.events.all()
    
    # Получаем связанные новости (того же дня или той же категории)
    related_news = (
        News.objects.filter(is_active=True)
        .filter(Q(news_date=news.news_date) | Q(category=news.category))
        .exclude(pk=news.pk)
        .select_related("category")
        .order_by("-news_date")[:4]
    )

    context = {
        "news": news,
        "events": events,
        "events_count": news.events_count,
        "related_news": related_news,
        "total_comments": news.total_comments,
        "avg_rating": news.avg_rating if news.avg_rating is not None else 0,
    }
    return render(request, "news/detail.html", context)
