from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from services.models import Service
from .cart import Cart
from django.contrib import messages

@require_POST
def cart_add(request, service_id):
    """
    Добавляет выбранную услугу в корзину пользователя.
    """
    cart = Cart(request)
    service = get_object_or_404(Service, id=service_id)
    cart.add(service=service)
    
    if 'HX-Request' in request.headers:
        return render(request, 'cart/detail_partial.html', {'cart': cart})
        
    messages.success(request, f'Услуга "{service.title}" добавлена в корзину')
    return redirect('cart:cart_detail')

@require_POST
def cart_remove(request, service_id):
    """
    Удаляет услугу из корзины.
    """
    cart = Cart(request)
    service = get_object_or_404(Service, id=service_id)
    cart.remove(service)
    
    if 'HX-Request' in request.headers:
        return render(request, 'cart/detail_partial.html', {'cart': cart})
        
    messages.info(request, f'Услуга "{service.title}" удалена из корзины')
    return redirect('cart:cart_detail')

def cart_detail(request):
    """
    Отображает страницу с деталями корзины и списком выбранных услуг.
    """
    cart = Cart(request)
    if 'HX-Request' in request.headers:
        return render(request, 'cart/detail_partial.html', {'cart': cart})
    return render(request, 'cart/detail.html', {'cart': cart})
