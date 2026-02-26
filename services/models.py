import re
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from tinymce.models import HTMLField

from main.utils import RenameUploadTo
from main.models import ActiveModel, SEOModel, TimestampModel
from accounts.models import User

# Регулярное выражение для контактных телефонов вынесено на уровень модуля
PHONE_PATTERN = re.compile(r'^\+?[1-9][\d\-\(\)\.\s]{9,20}$')

class Technology(models.Model):
    """Модель для хранения неограниченного стека технологий (веб-разработка, графика и т.д.)."""
    name = models.CharField(
        max_length=100, 
        unique=True,
        verbose_name=_("Название технологии/инструмента"),
        help_text=_("Например: Python, UI/UX Design, Docker, Figma")
    )
    
    class Meta:
        verbose_name = _("Технология")
        verbose_name_plural = _("Технологии")
        ordering = ["name"]

    def __str__(self):
        return self.name

class Service(ActiveModel, SEOModel, TimestampModel):
    """
    Модель услуги для предложения клиентам компании.
    Услуга включает развернутое описание, тарифы, 
    и указание стека технологий для предоставления результата.
    """
    title = models.CharField(
        max_length=200,
        verbose_name=_("Название услуги"),
        help_text=_("Максимальная длина - 200 символов")
    )
    slug = models.SlugField(
        unique=True,
        verbose_name=_("URL"),
        max_length=200,
        help_text=_("Уникальный идентификатор для URL")
    )
    icon = models.FileField(
        upload_to=RenameUploadTo("services/icons/"),
        verbose_name=_("Иконка (JPG/GIF/PNG/SVG)"),
        blank=True,
        null=True,
        help_text=_("Рекомендуемый размер: 64x64 или 128x128 пикселей")
    )
    short_description = HTMLField(
        verbose_name=_("Краткое описание"),
        blank=True,
        help_text=_("Краткое описание для отображения в списках/карточках")
    )
    description = HTMLField(
        verbose_name=_("Полное описание"),
        default=_("<p>Описание услуги</p>"),
        help_text=_("Подробное описание профиля услуги с использованием форматирования")
    )
    technologies = models.ManyToManyField(
        Technology,
        verbose_name=_("Стек технологий"),
        blank=True,
        related_name="services",
        help_text=_("Выберите неограниченное число технологий (веб-разработка, дизайн и др.)")
    )
    
    PRICE_TYPE_CHOICES = [
        ('fixed', _('Фиксированная')),
        ('range', _('От и До')),
        ('contact', _('По договоренности')),
    ]
    price_type = models.CharField(
        max_length=10,
        choices=PRICE_TYPE_CHOICES,
        default='fixed',
        verbose_name=_("Тип ценообразования")
    )
    price_fixed = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Фиксированная цена"),
        help_text=_("Итоговая цена (при фиксированной оплате)")
    )
    price_min = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Начальная цена (ОТ)"),
        help_text=_("Нижняя граница диапазона")
    )
    price_max = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Конечная цена (ДО)"),
        help_text=_("Верхняя граница диапазона")
    )
    
    CURRENCY_CHOICES = [
        ('RUB', _('Рубль (₽)')),
        ('USD', _('Доллар ($)')),
        ('EUR', _('Евро (€)')),
        ('KZT', _('Тенге (₸)')),
    ]
    currency = models.CharField(
        max_length=10,
        choices=CURRENCY_CHOICES,
        default="RUB",
        verbose_name=_("Валюта")
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Индекс сортировки"),
        help_text=_("Чем меньше номер, тем выше запись в каталоге")
    )
    is_popular = models.BooleanField(
        default=False,
        verbose_name=_("Популярная услуга (Хит продаж)"),
        help_text=_("Вывод услуги в спец-блоках с тегом 'популярное'")
    )
    is_available_for_order = models.BooleanField(
        default=True,
        verbose_name=_("Доступно для заказа"),
        help_text=_("Если отключено, вместо кнопки заказа будет выведено сообщение о временной недоступности")
    )
    estimated_time = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("Сроки выполнения"),
        help_text=_("Например: '2-3 недели', 'до 5 рабочих дней'")
    )
    views = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Просмотры"),
        editable=False
    )
    category = models.CharField(
        max_length=100,
        verbose_name=_("Категория (Тег)"),
        blank=True,
        help_text=_("Используется для группировки услуг (напр. Веб-разработка, Дизайн и др.)")
    )
    
    COMPLEXITY_CHOICES = [
        ('simple', _('Простой')),
        ('medium', _('Средний')),
        ('complex', _('Сложный')),
        ('expert', _('Ультра-кодинг')),
    ]
    complexity_level = models.CharField(
        max_length=50,
        verbose_name=_("Уровень сложности"),
        choices=COMPLEXITY_CHOICES,
        default='medium',
    )
    deliverables = HTMLField(
        verbose_name=_("Что будет в результате"),
        blank=True,
        help_text=_("Результат который отправляется заказчику на руки (файлы, макеты, код)")
    )
    
    class Meta:
        verbose_name = _("Услуга")
        verbose_name_plural = _("Услуги")
        ordering = ["order", "title"]
        indexes = [
            models.Index(fields=['order', 'is_active']),
            models.Index(fields=['is_popular', 'is_active']),
            models.Index(fields=['category', 'is_active']),
        ]

    def __str__(self):
        return f"{self.title}"

    @property
    def can_be_ordered(self):
        if not self.is_available_for_order:
            return False
        if self.price_type == 'fixed' and not self.price_fixed:
            return False
        return True

    def clean(self):
        """Инвариантная проверка модели перед записью в БД."""
        super().clean()
        
        # Обнуляем нерелевантные поля на основе типа цены:
        if self.price_type != 'fixed':
            self.price_fixed = None
        if self.price_type != 'range':
            self.price_min = None
            self.price_max = None
            
        if self.price_type == 'fixed' and not self.price_fixed:
            raise ValidationError({'price_fixed': _('Обязательно укажите фиксированную цену.')})
            
        elif self.price_type == 'range':
            if not self.price_min or not self.price_max:
                raise ValidationError(_('Для ценового диапазона нужно задать границы ОТ и ДО.'))
            if self.price_min >= self.price_max:
                raise ValidationError({'price_max': _('Цена ДО должна быть строго больше цены ОТ.')})

    def get_price_display(self):
        """Возвращает строку с красиво отформатированной ценой на основе типа."""
        currency_symbols = {'RUB': '₽', 'USD': '$', 'EUR': '€', 'KZT': '₸'}
        symbol = currency_symbols.get(self.currency, self.currency)
        
        if self.price_type == 'fixed' and self.price_fixed:
            formatted = f"{self.price_fixed:,.0f}".replace(',', ' ')
            return f"{formatted} {symbol}"
        
        elif self.price_type == 'range' and self.price_min and self.price_max:
            min_fmt = f"{self.price_min:,.0f}".replace(',', ' ')
            max_fmt = f"{self.price_max:,.0f}".replace(',', ' ')
            return f"от {min_fmt} до {max_fmt} {symbol}"
            
        elif self.price_type == 'contact':
            return _("Определяется индивидуально")
            
        return _("Уточняйте у менеджера")

    def get_tech_requirements_list(self):
        """Возращает список названий технологий для этой услуги из ManyToMany."""
        return [tech.name for tech in self.technologies.all()]

    def get_tech_requirements_display(self):
        """Названия технологий для отображения пользователю (массив)."""
        return self.get_tech_requirements_list()


class ServiceOrder(TimestampModel):
    """
    Модель оформления заказа услуги. 
    Собирает обратную связь или "лиды".
    """
    STATUS_CHOICES = [
        ("new", _("Новый")),
        ("confirmed", _("Подтвержден")),
        ("in_progress", _("Поступил в работу")),
        ("completed", _("Реализован/Выполнен")),
        ("cancelled", _("Отменен/Заморожен")),
    ]
    
    service = models.ForeignKey(
        Service,
        on_delete=models.PROTECT,
        verbose_name=_("Назначенная услуга"),
        related_name='orders'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Покупатель"),
        related_name='service_orders'
    )
    full_name = models.CharField(max_length=255, verbose_name=_("Имя покупателя"))
    phone = models.CharField(max_length=25, verbose_name=_("Номер связи"), help_text=_("Примерном: +7(900)123-45-67"))
    email = models.EmailField(verbose_name=_("Электронная почта"), max_length=255)
    message = models.TextField(
        verbose_name=_("Уточнения/Комментарий"),
        blank=True,
        help_text=_("Детальное разъяснение задачи клиентом")
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="new",
        verbose_name=_("Статус заявки")
    )
    admin_notes = models.TextField(
        verbose_name=_("Служебные пометки (невидимо клиенту)"),
        blank=True,
        help_text=_("Для внутренней коммуникации команды")
    )
    estimated_budget = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Указанный бюджет"),
    )
    deadline = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Желательный дедлайн")
    )

    class Meta:
        verbose_name = _("Заявка на услугу")
        verbose_name_plural = _("Заявки на услуги")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['service', 'status']),
        ]

    def __str__(self):
        return f"Заказ {self.short_id} - Услуга: {self.service.title}"

    @property
    def short_id(self):
        """Интуитивно понятный генератор идентификатора."""
        return f"ORD-{self.pk:06d}" if self.pk else "ORD-000000"

    def clean(self):
        """Базовая проверка телефона."""
        super().clean()
        
        if self.phone and not PHONE_PATTERN.match(self.phone):
            raise ValidationError({'phone': _('Разрешен только корректный телефонный формат (+7...).')})
            
        if self.estimated_budget is not None and self.estimated_budget < 0:
            raise ValidationError({'estimated_budget': _('Цена бюджета не может быть числом со знаком минус.')})

    def get_status_display_with_color(self):
        """Возвращает защищенный HTML-тег для вывода подсвеченного статуса."""
        colors = {
            'new': '#3498db',         # синий
            'confirmed': '#27ae60',   # зеленый-спокойный
            'in_progress': '#f39c12', # оранжевый
            'completed': '#8e44ad',   # фиолетовый
            'cancelled': '#e74c3c',   # ярко-красный
        }
        
        color = colors.get(self.status, '#7f8c8d')
        return format_html(
            '<span style="background-color: {}; color: #fff; padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; text-transform: uppercase;">{}</span>',
            color,
            self.get_status_display()
        )