from django.shortcuts import render, get_object_or_404, redirect
from .models import Page, SiteSettings
from .forms import ContactForm
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from news.models import News, NewsCategory
from portfolio.models import Portfolio, PortfolioCategory
from reviews.models import Review
from tickets.models import Ticket
from django.contrib.auth import get_user_model
from django.db.models import Sum

User = get_user_model()


def home(request):
    stats = {}
    if request.user.is_staff:
        news_views = News.objects.aggregate(total=Sum("views"))["total"] or 0
        portfolio_views = Portfolio.objects.aggregate(total=Sum("views"))["total"] or 0
        
        stats = {
            "news_count": News.objects.count(),
            "news_categories_count": NewsCategory.objects.count(),
            "portfolio_count": Portfolio.objects.count(),
            "portfolio_categories_count": PortfolioCategory.objects.count(),
            "reviews_count": Review.objects.count(),
            "pending_reviews_count": Review.objects.filter(status="pending").count(),
            "tickets_count": Ticket.objects.count(),
            "open_tickets_count": Ticket.objects.filter(status="open").count(),
            "users_count": User.objects.count(),
            "total_views": news_views + portfolio_views,
        }
    return render(request, "main/home.html", {"stats": stats})


def page_detail(request, slug):
    page = get_object_or_404(Page, slug=slug, is_active=True)
    form = None

    if slug == "kontakty":
        if request.method == "POST":
            form = ContactForm(request.POST)
            if form.is_valid():
                site_settings = SiteSettings.objects.filter(is_active=True).first()
                recipient = site_settings.site_email if site_settings and site_settings.site_email else settings.EMAIL_HOST_USER
                
                subject = f"Сообщение с сайта: {form.cleaned_data['name']}"
                message = f"""
                Имя: {form.cleaned_data['name']}
                Email: {form.cleaned_data['email']}
                Телефон: {form.cleaned_data['phone']}
                
                Сообщение:
                {form.cleaned_data['message']}
                """
                try:
                    send_mail(
                        subject,
                        message,
                        settings.DEFAULT_FROM_EMAIL,
                        [recipient],
                        fail_silently=False,
                    )
                    messages.success(request, "Ваше сообщение успешно отправлено!")
                    return redirect("main:page_detail", slug=slug)
                except Exception as e:
                    messages.error(request, f"Ошибка при отправке: {e}")
        else:
            form = ContactForm()

    return render(request, "main/page_detail.html", {"page": page, "form": form})


def page_not_found(request, exception):
    """Обработчик ошибки 404"""
    return render(request, "404.html", status=404)


def server_error(request):
    """Обработчик ошибки 500"""
    return render(request, "500.html", status=500)


def robots_txt(request):
    """Генерация robots.txt"""
    from django.conf import settings
    scheme = "https" if not settings.DEBUG else "http"
    host = request.get_host()
    return render(
        request,
        "robots.txt",
        {"scheme": scheme, "host": host},
        content_type="text/plain",
    )
