from django.urls import path
from . import views
from .feeds import LatestNewsFeed

app_name = "news"

urlpatterns = [
    path("", views.news_list, name="list"),  # news:list
    path("search/", views.news_search, name="search"),  # news:search
    path("category/<slug:category_slug>/", views.news_by_category, name="by_category"),
    path("feed/", LatestNewsFeed(), name="feed"),  # RSS лента
    path("<slug:slug>/", views.news_detail, name="detail"),
]
