from django.shortcuts import render, get_object_or_404
from .models import Portfolio, PortfolioCategory


def portfolio_list(request):
    portfolio_list = Portfolio.objects.filter(is_active=True)
    categories = PortfolioCategory.objects.filter(is_active=True)
    return render(
        request,
        "portfolio/list.html",
        {"portfolio_list": portfolio_list, "categories": categories},
    )


def portfolio_by_category(request, category_slug):
    category = get_object_or_404(PortfolioCategory, slug=category_slug, is_active=True)
    portfolio_list = Portfolio.objects.filter(category=category, is_active=True)
    categories = PortfolioCategory.objects.filter(is_active=True)
    return render(
        request,
        "portfolio/list.html",
        {
            "portfolio_list": portfolio_list,
            "categories": categories,
            "current_category": category,
        },
    )


def portfolio_detail(request, slug):
    portfolio = get_object_or_404(Portfolio, slug=slug, is_active=True)
    portfolio.increment_views()
    return render(request, "portfolio/detail.html", {"portfolio": portfolio})


def order_portfolio(request, portfolio_id):
    portfolio = get_object_or_404(Portfolio, id=portfolio_id, is_active=True)
    # Здесь будет логика оформления заказа
    return render(request, "portfolio/order.html", {"portfolio": portfolio})
