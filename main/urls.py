from django.urls import path
from . import views

app_name = "main"

urlpatterns = [
    path("", views.home, name="home"),  # Добавлено name='home'
    path("page/<slug:slug>/", views.page_detail, name="page_detail"),
]
