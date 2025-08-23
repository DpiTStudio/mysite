from django.shortcuts import render, get_object_or_404
from django.db.models import Count
from .models import News, NewsCategory


def news_list(request):
    news_list = News.objects.filter(is_active=True).select_related("category")
    categories = NewsCategory.objects.filter(is_active=True).annotate(
        news_count=Count("news")
    )

    return render(
        request, "news/list.html", {"news_list": news_list, "categories": categories}
    )


def news_by_category(request, category_slug):
    category = get_object_or_404(NewsCategory, slug=category_slug, is_active=True)
    news_list = News.objects.filter(category=category, is_active=True).select_related(
        "category"
    )
    categories = NewsCategory.objects.filter(is_active=True).annotate(
        news_count=Count("news")
    )

    return render(
        request,
        "news/list.html",
        {
            "news_list": news_list,
            "categories": categories,
            "current_category": category,
        },
    )


def news_detail(request, slug):
    news = get_object_or_404(News, slug=slug, is_active=True)
    news.increment_views()

    # Получаем похожие новости из той же категории
    related_news = News.objects.filter(category=news.category, is_active=True).exclude(
        id=news.id
    )[:3]

    return render(
        request, "news/detail.html", {"news": news, "related_news": related_news}
    )
