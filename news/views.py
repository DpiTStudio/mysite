from django.shortcuts import render, get_object_or_404
from .models import News, NewsCategory


def news_list(request):
    news_list = News.objects.filter(is_active=True)
    categories = NewsCategory.objects.filter(is_active=True)
    return render(
        request, "news/list.html", {"news_list": news_list, "categories": categories}
    )


def news_by_category(request, category_slug):
    category = get_object_or_404(NewsCategory, slug=category_slug, is_active=True)
    news_list = News.objects.filter(category=category, is_active=True)
    categories = NewsCategory.objects.filter(is_active=True)
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
    return render(request, "news/detail.html", {"news": news})
