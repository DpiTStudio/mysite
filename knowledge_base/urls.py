from django.urls import path
from . import views

app_name = 'knowledge_base'

urlpatterns = [
    path('', views.index, name='index'),
    path('category/<slug:slug>/', views.category_detail, name='category'),
    path('article/<slug:slug>/', views.article_detail, name='article'),
]
