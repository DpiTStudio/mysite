from django.urls import path
from django.views.generic import RedirectView
from . import views

app_name = 'knowledge_base'

urlpatterns = [
    path('', views.index, name='index'),
    path('category/', RedirectView.as_view(pattern_name="knowledge_base:index", permanent=False)),
    path('category/<slug:slug>/', views.category_detail, name='category'),
    path('article/', RedirectView.as_view(pattern_name="knowledge_base:index", permanent=False)),
    path('article/<slug:slug>/', views.article_detail, name='article'),
]
