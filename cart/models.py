from django.db import models
from django.utils.translation import gettext_lazy as _
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
    service = models.ForeignKey(Service, related_name='order_items', on_delete=models.PROTECT, verbose_name=_("Услуга"))
    price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name=_("Цена (фикс)"))
    quantity = models.PositiveIntegerField(default=1, verbose_name=_("Количество"))

    class Meta:
        verbose_name = _("Товар/Услуга в заказе")
        verbose_name_plural = _("Товары/Услуги в заказах")

    def __str__(self):
        return str(self.id)

    def get_cost(self):
        return self.price * self.quantity
