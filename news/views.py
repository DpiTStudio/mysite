from django.shortcuts import render, get_object_or_404
from django.db.models import Count, Q
from django.core.paginator import Paginator
from .models import News, NewsCategory


def news_list(request):
    news_list = News.objects.filter(is_active=True).select_related("category")
    categories = NewsCategory.objects.filter(is_active=True).annotate(
        news_count=Count("news")
    )

    # Пагинация
    paginator = Paginator(news_list, 9)  # 9 новостей на страницу
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "news/list.html",
        {
            "page_obj": page_obj,
            "categories": categories,
            "news_per_row": 3,  # 3 новости в ряду
        },
    )


def news_by_category(request, category_slug):
    category = get_object_or_404(NewsCategory, slug=category_slug, is_active=True)
    news_list = News.objects.filter(category=category, is_active=True).select_related(
        "category"
    )
    categories = NewsCategory.objects.filter(is_active=True).annotate(
        news_count=Count("news")
    )

    # Пагинация
    paginator = Paginator(news_list, 9)  # 9 новостей на страницу
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "news/list.html",
        {
            "page_obj": page_obj,
            "categories": categories,
            "current_category": category,
            "news_per_row": 3,  # 3 новости в ряду
        },
    )


def news_detail(request, slug):
    news = get_object_or_404(News, slug=slug, is_active=True)
    news.increment_views()

    # Получаем похожие новости из той же категории
    related_news = News.objects.filter(category=news.category, is_active=True).exclude(
        id=news.id
    )[:3]

    # Навигация между новостями
    previous_news = (
        News.objects.filter(is_active=True, created_at__lt=news.created_at)
        .order_by("-created_at")
        .first()
    )

    next_news = (
        News.objects.filter(is_active=True, created_at__gt=news.created_at)
        .order_by("created_at")
        .first()
    )

    return render(
        request,
        "news/detail.html",
        {
            "news": news,
            "related_news": related_news,
            "previous_news": previous_news,
            "next_news": next_news,
        },
    )
