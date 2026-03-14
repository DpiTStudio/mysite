from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from services.models import Service
from accounts.models import User

class Order(models.Model):
    first_name = models.CharField(max_length=50, verbose_name=_("Имя"))
    last_name = models.CharField(max_length=50, verbose_name=_("Фамилия"), blank=True)
    email = models.EmailField(verbose_name=_("Email"))
    phone = models.CharField(max_length=20, verbose_name=_("Телефон"))
    company = models.CharField(max_length=100, blank=True, verbose_name=_("Компания"))
    comment = models.TextField(blank=True, verbose_name=_("Комментарий к заказу"), help_text=_("Дополнительная информация о проекте или пожелания"))
    
    created = models.DateTimeField(auto_now_add=True, verbose_name=_("Создан"))
    updated = models.DateTimeField(auto_now=True, verbose_name=_("Обновлен"))
    paid = models.BooleanField(default=False, verbose_name=_("Оплачен"))
    
    # Optional connection to registered user
    user = models.ForeignKey(User, related_name='orders', on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Покупатель/Клиент"))

    STATUS_CHOICES = [
        ("new", _("Новый")),
        ("confirmed", _("Подтвержден")),
        ("in_progress", _("Поступил в работу")),
        ("completed", _("Реализован/Выполнен")),
        ("cancelled", _("Отменен")),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="new",
        verbose_name=_("Статус заказа")
    )

    class Meta:
        ordering = ('-created',)
        verbose_name = _("Заказ (Корзина)")
        verbose_name_plural = _("Заказы сайтов/услуг")

    def __str__(self):
        return f'Заказ #{self.id}'

    def get_total_cost(self):
        return sum(item.get_cost() for item in self.items.all())

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE, verbose_name=_("Заказ"))
    service = models.ForeignKey(Service, related_name='order_items', on_delete=models.PROTECT, verbose_name=_("Услуга"), null=True, blank=True)
    portfolio = models.ForeignKey('portfolio.Portfolio', related_name='order_items', on_delete=models.PROTECT, verbose_name=_("Работа (Портфолио)"), null=True, blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name=_("Цена (фикс)"), null=True, blank=True)
    price_type = models.CharField(max_length=10, default='fixed', verbose_name=_("Тип цены"))
    price_min = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name=_("Начальная цена"))
    price_max = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name=_("Конечная цена"))
    quantity = models.PositiveIntegerField(default=1, verbose_name=_("Количество"))

    class Meta:
        verbose_name = _("Товар/Услуга в заказе")
        verbose_name_plural = _("Товары/Услуги в заказах")

    def __str__(self):
        return str(self.id)

    def get_cost(self):
        if self.price_type == 'fixed' and self.price is not None:
            return self.price * self.quantity
        return 0

    def get_price_display(self):
        if self.price_type == 'fixed' and self.price is not None:
            return f"{self.price} ₽"
        elif self.price_type == 'range' and self.price_min and self.price_max:
            return f"от {self.price_min} до {self.price_max} ₽"
        else:
            return "По договоренности"


class PromoCode(models.Model):
    """
    Промокод для скидки в корзине.
    Поддерживает 2 типа: процентную скидку и фиксированную сумму.
    """

    DISCOUNT_TYPE_CHOICES = [
        ('percent', _('Процент (%)')),
        ('fixed', _('Фиксированная сумма (₽)')),
    ]

    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name=_('Промокод'),
        help_text=_('Латинские буквы, цифры. Например: SUMMER2025')
    )
    discount_type = models.CharField(
        max_length=10,
        choices=DISCOUNT_TYPE_CHOICES,
        default='percent',
        verbose_name=_('Тип скидки')
    )
    discount_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_('Размер скидки'),
        help_text=_('Для процентов — значение 1–100, для фиксированной суммы — в рублях')
    )
    valid_from = models.DateTimeField(
        default=timezone.now,
        verbose_name=_('Действителен с')
    )
    valid_until = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Действителен до'),
        help_text=_('Оставьте пустым для бессрочного промокода')
    )
    max_uses = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Макс. кол-во активаций'),
        help_text=_('0 — безлимитно')
    )
    current_uses = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Текущее кол-во активаций'),
        editable=False
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Активен')
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Создан'))

    class Meta:
        verbose_name = _('Промокод')
        verbose_name_plural = _('Промокоды')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.code} ({self.get_discount_type_display()}: {self.discount_value})'

    def is_valid(self):
        """True, если промокод активен, не истёк срок и не исчерпан лимит."""
        now = timezone.now()
        if not self.is_active:
            return False
        if self.valid_from and self.valid_from > now:
            return False
        if self.valid_until and self.valid_until < now:
            return False
        if self.max_uses > 0 and self.current_uses >= self.max_uses:
            return False
        return True

    def apply_discount(self, total):
        """Returns сумму скидки (decimal) для данной стоимости."""
        from decimal import Decimal
        if self.discount_type == 'percent':
            return (total * self.discount_value / Decimal('100')).quantize(Decimal('0.01'))
        else:  # fixed
            return min(self.discount_value, total)


class PromoCodeUsage(models.Model):
    """Oтслеживает кто и когда использовал промокод."""
    promo_code = models.ForeignKey(
        PromoCode,
        on_delete=models.CASCADE,
        related_name='usages',
        verbose_name=_('Промокод')
    )
    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name='promo_usage',
        verbose_name=_('Заказ')
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('Пользователь')
    )
    discount_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name=_('Сумма скидки')
    )
    used_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата использования'))

    class Meta:
        verbose_name = _('Использование промокода')
        verbose_name_plural = _('История промокодов')

    def __str__(self):
        return f'{self.promo_code.code} — Заказ #{self.order.id}'
