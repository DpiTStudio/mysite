from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.cart_detail, name='cart_detail'),
    path('add/<str:item_type>/<int:item_id>/', views.cart_add, name='cart_add'),
    path('remove/<str:item_type>/<int:item_id>/', views.cart_remove, name='cart_remove'),
    path('checkout/', views.order_create, name='order_create'),
    path('success/<int:order_id>/', views.order_success, name='order_success'),
]
