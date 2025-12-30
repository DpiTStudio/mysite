from django.shortcuts import render, get_object_or_404
from django.http import Http404
from .models import Page


def home(request):
    return render(request, "main/home.html")


def page_detail(request, slug):
    page = get_object_or_404(Page, slug=slug, is_active=True)
    return render(request, "main/page_detail.html", {"page": page})


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
