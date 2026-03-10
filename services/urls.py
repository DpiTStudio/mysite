from django.urls import path
from django.views.generic import RedirectView
from . import views

app_name = 'services'

urlpatterns = [
    path('', views.ServiceListView.as_view(), name='list'),
    path('search/', views.ServiceSearchView.as_view(), name='search'),
    path('<slug:slug>/', views.ServiceDetailView.as_view(), name='detail'),
    path('order/', RedirectView.as_view(pattern_name="services:list", permanent=False)),
    path('order/<slug:slug>/', views.ServiceOrderView.as_view(), name='order'),
]
