from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from services.models import Service
from portfolio.models import Portfolio
from .cart import Cart
from django.contrib import messages
from .models import OrderItem, Order
from .forms import OrderCreateForm

@require_POST
def cart_add(request, item_type, item_id):
    """
    Добавляет выбранную услугу или работу в корзину пользователя.
    """
    cart = Cart(request)
    if item_type == 'service':
        item = get_object_or_404(Service, id=item_id)
    else:
        item = get_object_or_404(Portfolio, id=item_id)
        
    if not getattr(item, 'is_available_for_order', True):
        messages.error(request, f'К сожалению, "{item.title}" временно недоступно для заказа.')
        return redirect(request.META.get('HTTP_REFERER', 'main:home'))
        
    cart.add(item=item, item_type=item_type)
    
    if 'HX-Request' in request.headers:
        return render(request, 'cart/detail_partial.html', {'cart': cart})
        
    messages.success(request, f'"{item.title}" добавлено в корзину')
    return redirect('cart:cart_detail')

@require_POST
def cart_remove(request, item_type, item_id):
    """
    Удаляет элемент из корзины.
    """
    cart = Cart(request)
    cart.remove(item_type=item_type, item_id=item_id)
    
    if 'HX-Request' in request.headers:
        return render(request, 'cart/detail_partial.html', {'cart': cart})
        
    messages.info(request, 'Элемент удален из корзины')
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
                if item['item_type'] == 'service':
                    OrderItem.objects.create(
                        order=order,
                        service=item['item_obj'],
                        price=item['price'],
                        quantity=item['quantity']
                    )
                else:
                    OrderItem.objects.create(
                        order=order,
                        portfolio=item['item_obj'],
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
