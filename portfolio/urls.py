from django.urls import path
from . import views

app_name = "portfolio"

urlpatterns = [
    path("", views.portfolio_list, name="list"),  # portfolio:list
    path(
        "category/<slug:category_slug>/",
        views.portfolio_by_category,
        name="by_category",
    ),
    path("<slug:slug>/", views.portfolio_detail, name="detail"),
    path("order/<int:portfolio_id>/", views.order_portfolio, name="order"),
]
