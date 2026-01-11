from django.shortcuts import render, get_object_or_404
from django.db.models import Count
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Portfolio, PortfolioCategory



def get_latest_portfolio():
    """Функция для получения последних 3 активных портфолио"""
    return (
        Portfolio.objects.filter(is_active=True)
        .select_related("category")
        .order_by("-created_at")[:3]
    )


def portfolio_list(request):
    """
    Список всех портфолио с пагинацией
    """
    portfolio_queryset = (
        Portfolio.objects.filter(is_active=True)
        .select_related("category")
        .order_by("-created_at")
    )
    categories = PortfolioCategory.objects.filter(is_active=True).annotate(
        portfolio_count=Count("portfolio")
    )

    # Пагинация - 9 на страницу
    paginator = Paginator(portfolio_queryset, 9)
    page = request.GET.get("page")

    try:
        portfolio_list = paginator.page(page)
    except PageNotAnInteger:
        portfolio_list = paginator.page(1)
    except EmptyPage:
        portfolio_list = paginator.page(paginator.num_pages)

    return render(
        request,
        "portfolio/list.html",
        {
            "portfolio_list": portfolio_list,
            "categories": categories,
            "latest_portfolio": get_latest_portfolio(),
        },
    )





def portfolio_by_category(request, category_slug):
    """
    Портфоли по категории с пагинацией
    """
    category = get_object_or_404(PortfolioCategory, slug=category_slug, is_active=True)
    portfolio_queryset = (
        Portfolio.objects.filter(category=category, is_active=True)
        .select_related("category")
        .order_by("-created_at")
    )

    categories = PortfolioCategory.objects.filter(is_active=True).annotate(
        portfolio_count=Count("portfolio")
    )

    # Пагинация - 9 новостей на страницу
    paginator = Paginator(portfolio_queryset, 9)
    page = request.GET.get("page")

    try:
        portfolio_list = paginator.page(page)
    except PageNotAnInteger:
        portfolio_list = paginator.page(1)
    except EmptyPage:
        portfolio_list = paginator.page(paginator.num_pages)

    return render(
        request,
        "portfolio/list.html",
        {
            "portfolio_list": portfolio_list,
            "categories": categories,
            "current_category": category,
            "latest_portfolio": get_latest_portfolio(),
        },
    )


def portfolio_detail(request, slug):
    """
    Детальная страница
    """
    portfolio = get_object_or_404(Portfolio, slug=slug, is_active=True)
    portfolio.increment_views()

    categories = PortfolioCategory.objects.filter(is_active=True).annotate(
        portfolio_count=Count("portfolio")
    )

    # Получаем похожие портфолио из той же категории
    related_portfolio = (
        Portfolio.objects.filter(category=portfolio.category, is_active=True)
        .exclude(id=portfolio.id)
        .order_by("-created_at")[:3]
    )

    return render(
        request,
        "portfolio/detail.html",
        {
            "portfolio": portfolio,
            "related_portfolio": related_portfolio,
            "latest_portfolio": get_latest_portfolio(),
            "categories": categories,
        },
    )

