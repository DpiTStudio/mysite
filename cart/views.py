from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from services.models import Service
from .cart import Cart
from django.contrib import messages

@require_POST
def cart_add(request, service_id):
    cart = Cart(request)
    service = get_object_or_404(Service, id=service_id)
    cart.add(service=service)
    messages.success(request, f'Услуга "{service.title}" добавлена в корзину')
    return redirect('cart:cart_detail')

def cart_remove(request, service_id):
    cart = Cart(request)
    service = get_object_or_404(Service, id=service_id)
    cart.remove(service)
    messages.info(request, f'Услуга "{service.title}" удалена из корзины')
    return redirect('cart:cart_detail')

def cart_detail(request):
    cart = Cart(request)
    return render(request, 'cart/detail.html', {'cart': cart})
