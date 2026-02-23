from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from services.models import Service
from .cart import Cart
from django.contrib import messages
from .models import OrderItem, Order
from .forms import OrderCreateForm

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

def order_create(request):
    cart = Cart(request)
    if not cart:
        messages.warning(request, "Ваша корзина пуста.")
        return redirect('cart:cart_detail')

    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            if request.user.is_authenticated:
                order.user = request.user
            order.save()
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    service=item['service'],
                    price=item['price'],
                    quantity=item['quantity']
                )
            # очистка корзины
            cart.clear()
            # Добавление сообщения пользователю
            messages.success(request, "Заказ успешно оформлен!")
            # Можно отправить письмо админу или юзеру
            return redirect('cart:order_success', order_id=order.id)
    else:
        initial_data = {}
        if request.user.is_authenticated:
            initial_data = {
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'email': request.user.email,
                'phone': getattr(request.user, 'profile', {}).get('phone_number', '') if hasattr(request.user, 'profile') else '',
            }
        form = OrderCreateForm(initial=initial_data)
        
    return render(request, 'cart/checkout.html', {'cart': cart, 'form': form})

def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    # Позволяем просмотр заказа только владельцу или админу
    if order.user and order.user != request.user and not request.user.is_superuser:
         return redirect('main:home')
    return render(request, 'cart/order_success.html', {'order': order})
