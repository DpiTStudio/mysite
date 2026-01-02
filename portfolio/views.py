from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Count
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
from .models import Portfolio, PortfolioCategory
from .forms import ServiceOrderForm


def get_latest_portfolio():
    """Функция для получения последних 3 активных портфолио"""
    return (
        Portfolio.objects.filter(is_active=True, is_service=False)
        .select_related("category")
        .order_by("-created_at")[:3]
    )


def portfolio_list(request):
    """
    Список всех портфолио с пагинацией
    """
    portfolio_queryset = (
        Portfolio.objects.filter(is_active=True, is_service=False)
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


def price_list(request):
    """
    Прайс-лист услуг
    """
    services = Portfolio.objects.filter(is_active=True, is_service=True).select_related("category")
    categories = PortfolioCategory.objects.filter(is_active=True, portfolio__is_service=True).distinct()
    
    form = ServiceOrderForm()
    
    if request.method == "POST":
        service_id = request.POST.get("service_id")
        service = get_object_or_404(Portfolio, id=service_id, is_service=True)
        form = ServiceOrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.service = service
            order.save()
            messages.success(request, f"Ваш заказ на услугу '{service.title}' успешно отправлен!")
            return redirect("portfolio:price_list")
        else:
            messages.error(request, "Пожалуйста, исправьте ошибки в форме.")

    return render(
        request,
        "portfolio/price_list.html",
        {
            "services": services,
            "categories": categories,
            "form": form,
        },
    )


def portfolio_by_category(request, category_slug):
    """
    Портфоли по категории с пагинацией
    """
    category = get_object_or_404(PortfolioCategory, slug=category_slug, is_active=True)
    portfolio_queryset = (
        Portfolio.objects.filter(category=category, is_active=True, is_service=False)
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

    # Получаем похожие портфолио из той же категории
    related_portfolio = (
        Portfolio.objects.filter(category=portfolio.category, is_active=True, is_service=portfolio.is_service)
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
        },
    )

