import json
import logging
import secrets
import string

from django.contrib import messages
from django.contrib.auth import login
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from accounts.models import User
from portfolio.models import Portfolio
from services.models import Service
from .cart import Cart
from .forms import OrderCreateForm
from .models import OrderItem, Order, PromoCode, PromoCodeUsage

logger = logging.getLogger(__name__)


# ────────────────────────────────────────────────────────────────────────────────
# Вспомогательные функции
# ────────────────────────────────────────────────────────────────────────────────

def _generate_password(length=12):
    """Генерация надёжного случайного пароля."""
    alphabet = string.ascii_letters + string.digits + "!@#$%"
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def _auto_register_client(email, first_name, last_name, phone):
    """
    Автоматически создаёт учётную запись для клиента (гостя),
    если пользователь с таким email ещё не зарегистрирован.

    Returns:
        (user: User | None, password: str | None, created: bool)
    """
    # Проверяем, существует ли пользователь с таким email
    existing = User.objects.filter(email=email).first()
    if existing:
        return existing, None, False

    # Генерируем username из email (до символа @)
    base_username = email.split('@')[0]
    username = base_username
    counter = 1
    while User.objects.filter(username=username).exists():
        username = f"{base_username}{counter}"
        counter += 1

    raw_password = _generate_password()
    user = User.objects.create_user(
        username=username,
        email=email,
        password=raw_password,
        first_name=first_name,
        last_name=last_name or '',
        phone=phone,
    )
    return user, raw_password, True


def _send_order_confirmation(request, order, auto_password=None):
    """
    Отправляет клиенту письмо с подтверждением заказа.
    Если auto_password передан — включает данные для входа.
    """
    try:
        from django.core.mail import send_mail
        from django.conf import settings

        subject = f"Ваш заказ #{order.id} принят"
        items_text = "\n".join(
            f"  • {item.get_item_title()} — {item.get_price_display()} × {item.quantity}"
            for item in order.items.all()
        )

        body_lines = [
            f"Здравствуйте, {order.first_name}!",
            "",
            f"Ваш заказ #{order.id} успешно оформлен.",
            f"Дата: {order.created.strftime('%d.%m.%Y %H:%M')}",
            "",
            "Состав заказа:",
            items_text,
        ]

        if order.discount_amount:
            body_lines += [
                "",
                f"Промокод: {order.promo_code_applied}",
                f"Скидка: {order.discount_amount} ₽",
                f"Итого со скидкой: {order.get_final_cost()} ₽",
            ]

        if auto_password:
            body_lines += [
                "",
                "─" * 40,
                "Мы автоматически создали для вас личный кабинет:",
                f"  Логин: {order.user.username}",
                f"  Пароль: {auto_password}",
                "",
                f"Войти в кабинет: {request.build_absolute_uri('/accounts/login/')}",
                "Рекомендуем сменить пароль после первого входа.",
            ]

        body_lines += [
            "",
            "─" * 40,
            "С вами свяжется менеджер для уточнения деталей.",
            "",
            "С уважением,",
            "Команда DPIT",
        ]

        send_mail(
            subject=subject,
            message="\n".join(body_lines),
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@dpit.ru'),
            recipient_list=[order.email],
            fail_silently=True,
        )
    except Exception as exc:
        logger.warning("Не удалось отправить письмо подтверждения заказа #%s: %s", order.id, exc)


# ────────────────────────────────────────────────────────────────────────────────
# Views
# ────────────────────────────────────────────────────────────────────────────────

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

    if not getattr(item, 'can_be_ordered', getattr(item, 'is_available_for_order', True)):
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
    """
    Оформление заказа:
    - предзаполняет форму данными авторизованного пользователя
    - при POST сохраняет заказ, применяет промокод из сессии,
      при необходимости авторегистрирует клиента и отправляет email.
    """
    cart = Cart(request)
    if not cart:
        messages.warning(request, "Ваша корзина пуста.")
        return redirect('cart:cart_detail')

    # Данные о применённом промокоде из сессии
    promo_code_str = request.session.get('promo_code', '')
    promo_obj = None
    promo_discount = None
    if promo_code_str:
        try:
            promo_obj = PromoCode.objects.get(code=promo_code_str)
            if promo_obj.is_valid():
                promo_discount = promo_obj.apply_discount(cart.get_total_price())
            else:
                promo_obj = None
                request.session.pop('promo_code', None)
        except PromoCode.DoesNotExist:
            request.session.pop('promo_code', None)

    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            auto_password = None
            auto_created = False

            # ── Привязка к пользователю ──────────────────────────────────────
            if request.user.is_authenticated:
                order.user = request.user
            elif form.cleaned_data.get('auto_register'):
                # Авторегистрация нового клиента
                user, auto_password, auto_created = _auto_register_client(
                    email=form.cleaned_data['email'],
                    first_name=form.cleaned_data['first_name'],
                    last_name=form.cleaned_data.get('last_name', ''),
                    phone=form.cleaned_data['phone'],
                )
                order.user = user
                order.auto_registered = auto_created
                if auto_created:
                    # Авторизуем нового пользователя
                    login(request, user, backend='django.contrib.auth.backends.ModelBackend')

            # ── Промокод ─────────────────────────────────────────────────────
            if promo_obj and promo_discount is not None:
                order.promo_code_applied = promo_obj.code
                order.discount_amount = promo_discount

            order.save()

            # ── Позиции заказа ───────────────────────────────────────────────
            for item in cart:
                kwargs = dict(
                    order=order,
                    price=item.get('price'),
                    price_type=item.get('price_type', 'fixed'),
                    price_min=item.get('price_min'),
                    price_max=item.get('price_max'),
                    quantity=item['quantity'],
                )
                if item['item_type'] == 'service':
                    kwargs['service'] = item['item_obj']
                else:
                    kwargs['portfolio'] = item['item_obj']
                OrderItem.objects.create(**kwargs)

            # ── Промокод: фиксируем использование ───────────────────────────
            if promo_obj and promo_discount is not None:
                PromoCodeUsage.objects.get_or_create(
                    order=order,
                    defaults=dict(
                        promo_code=promo_obj,
                        user=order.user,  # может быть None для гостя
                        discount_amount=promo_discount,
                    ),
                )
                promo_obj.current_uses += 1
                promo_obj.save(update_fields=['current_uses'])
                request.session.pop('promo_code', None)

            # ── Очистка корзины ──────────────────────────────────────────────
            cart.clear()

            # ── Email подтверждение ──────────────────────────────────────────
            _send_order_confirmation(request, order, auto_password=auto_password)

            # ── Сообщение пользователю ───────────────────────────────────────
            if auto_created:
                messages.success(
                    request,
                    f"Заказ #{order.id} оформлен! Для вас создан личный кабинет. "
                    f"Данные для входа отправлены на {order.email}."
                )
            else:
                messages.success(request, f"Заказ #{order.id} успешно оформлен!")

            # Передаём флаг авторегистрации через сессию для отображения на странице успеха
            request.session['order_auto_registered'] = auto_created
            request.session['order_auto_password'] = auto_password or ''

            return redirect('cart:order_success', order_id=order.id)
    else:
        # Предзаполнение формы данными авторизованного пользователя
        initial_data = {}
        if request.user.is_authenticated:
            initial_data = {
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'email': request.user.email,
                'phone': getattr(request.user, 'phone', ''),
            }
        form = OrderCreateForm(initial=initial_data)

    context = {
        'cart': cart,
        'form': form,
        'promo_obj': promo_obj,
        'promo_discount': promo_discount,
    }
    return render(request, 'cart/checkout.html', context)


def order_success(request, order_id):
    """
    Страница успешного оформления заказа.
    Доступна: владельцу заказа, суперпользователю или анонимному гостю
    (только сразу после оформления — пока order_id совпадает).
    """
    order = get_object_or_404(Order, id=order_id)

    # Защита: чужой заказ не показываем
    if order.user and request.user.is_authenticated:
        if order.user != request.user and not request.user.is_superuser:
            messages.error(request, "У вас нет доступа к этому заказу.")
            return redirect('main:home')
    elif order.user and not request.user.is_authenticated:
        # Заказ привязан к пользователю, но мы не авторизованы — ОК только если только что авторег
        pass

    # Получаем данные авторегистрации из сессии
    auto_registered = request.session.pop('order_auto_registered', False)
    auto_password = request.session.pop('order_auto_password', '')

    context = {
        'order': order,
        'auto_registered': auto_registered,
        'auto_password': auto_password,
    }
    return render(request, 'cart/order_success.html', context)


@require_POST
def apply_promo(request):
    """
    AJAX-endpoint для проверки и применения промокода.
    Хранит промокод в сессии до оформления заказа.
    """
    try:
        body = json.loads(request.body)
        code = body.get('code', '').strip().upper()
    except (json.JSONDecodeError, AttributeError):
        code = request.POST.get('code', '').strip().upper()

    if not code:
        return JsonResponse({'success': False, 'error': 'Введите промокод'}, status=400)

    try:
        promo = PromoCode.objects.get(code=code)
    except PromoCode.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Промокод не найден'}, status=404)

    if not promo.is_valid():
        return JsonResponse({'success': False, 'error': 'Промокод недействителен или истёк его срок'}, status=400)

    # Сохраняем промокод в сессии
    request.session['promo_code'] = code

    cart = Cart(request)
    total = cart.get_total_price()
    discount = float(promo.apply_discount(total)) if total else 0

    discount_label = (
        f'{promo.discount_value} %'
        if promo.discount_type == 'percent'
        else f'{promo.discount_value} ₽'
    )

    return JsonResponse({
        'success': True,
        'message': f'Промокод применён! Скидка: {discount_label}',
        'discount': discount,
        'discount_label': discount_label,
        'code': promo.code,
    })


@require_POST
def remove_promo(request):
    """Отменить промокод из сессии."""
    request.session.pop('promo_code', None)
    return JsonResponse({'success': True})
