from django.shortcuts import render, get_object_or_404
from .models import Page


def home(request):
    return render(request, "main/home.html")


def page_detail(request, slug):
    page = get_object_or_404(Page, slug=slug, is_active=True)
    return render(request, "main/page_detail.html", {"page": page})
