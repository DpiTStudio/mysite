from django.urls import path
from django.views.generic import RedirectView
from . import views

app_name = "portfolio"

urlpatterns = [
    path("", views.portfolio_list, name="list"),

    path("category/", RedirectView.as_view(pattern_name="portfolio:list", permanent=False)),
    path(
        "category/<slug:category_slug>/",
        views.portfolio_by_category,
        name="by_category",
    ),
    path("<slug:slug>/", views.portfolio_detail, name="detail"),
]
