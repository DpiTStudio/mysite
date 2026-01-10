from django.db import models
from django.core.exceptions import ValidationError
from tinymce.models import HTMLField
from main.utils import RenameUploadTo
from main.models import ActiveModel, SEOModel, TimestampModel
from accounts.models import User
from django.utils.translation import gettext_lazy as _
import re


# Константы для выбора технологий
TECH_CHOICES = [
    ('html', 'HTML/CSS'),
    ('js', 'JavaScript'),
    ('python', 'Python'),
    ('php', 'PHP'),
    ('mobile', 'Мобильная версия'),
    ('adaptive', 'Адаптивная верстка'),
    ('seo', 'SEO-оптимизация'),
]


class Service(ActiveModel, SEOModel, TimestampModel):
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
        help_text=_("Краткое описание для превью")
    )
    
    description = HTMLField(
        verbose_name=_("Полное описание"),
        default=_("<p>Описание услуги</p>"),
        help_text=_("Подробное описание услуги с возможностью форматирования")
    )
    
    technical_requirements = models.TextField(
        verbose_name=_("Технические требования"),
        blank=True,
        help_text=_("Перечислите технологии через запятую")
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
        verbose_name=_("Тип цены")
    )
    
    price_fixed = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Фиксированная цена"),
        help_text=_("Цена в указанной валюте")
    )
    
    price_min = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Цена ОТ"),
        help_text=_("Минимальная цена диапазона")
    )
    
    price_max = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Цена ДО"),
        help_text=_("Максимальная цена диапазона")
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
        verbose_name=_("Порядок сортировки"),
        help_text=_("Чем меньше число, тем выше в списке")
    )
    
    is_popular = models.BooleanField(
        default=False,
        verbose_name=_("Популярная услуга"),
        help_text=_("Отображать в блоке популярных услуг")
    )
    
    estimated_time = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("Примерные сроки"),
        help_text=_("Например: 3-5 дней, 2 недели и т.д.")
    )

    class Meta:
        verbose_name = _("Услуга")
        verbose_name_plural = _("Услуги")
        ordering = ["order", "title"]
        indexes = [
            models.Index(fields=['order', 'is_active']),
            models.Index(fields=['is_popular', 'is_active']),
        ]

    def __str__(self):
        return self.title

    def clean(self):
        """Валидация данных модели"""
        super().clean()
        
        # Проверка цен в зависимости от типа
        if self.price_type == 'fixed':
            if not self.price_fixed:
                raise ValidationError({'price_fixed': _('Для фиксированной цены необходимо указать фиксированную цену.')})
            if self.price_min or self.price_max:
                raise ValidationError(_('Для фиксированной цены не нужно указывать минимальную и максимальную цены.'))
        
        elif self.price_type == 'range':
            if not self.price_min or not self.price_max:
                raise ValidationError(_('Для цены диапазоном необходимо указать обе цены: ОТ и ДО.'))
            if self.price_min >= self.price_max:
                raise ValidationError({'price_max': _('Цена ДО должна быть больше цены ОТ.')})
        
        # Удаляем ненужные значения цен
        if self.price_type != 'fixed':
            self.price_fixed = None
        if self.price_type != 'range':
            self.price_min = None
            self.price_max = None

    def get_price_display(self):
        """Форматированное отображение цены"""
        if self.price_type == 'fixed' and self.price_fixed:
            currency_symbols = {'RUB': '₽', 'USD': '$', 'EUR': '€', 'KZT': '₸'}
            symbol = currency_symbols.get(self.currency, self.currency)
            return f"{self.price_fixed:,.0f} {symbol}".replace(',', ' ')
        
        elif self.price_type == 'range' and self.price_min and self.price_max:
            currency_symbols = {'RUB': '₽', 'USD': '$', 'EUR': '€', 'KZT': '₸'}
            symbol = currency_symbols.get(self.currency, self.currency)
            return f"от {self.price_min:,.0f} до {self.price_max:,.0f} {symbol}".replace(',', ' ')
        
        elif self.price_type == 'contact':
            return _("По договоренности")
        
        return _("Цена не указана")

    def get_tech_requirements_list(self):
        """Возвращает список кодов выбранных технологий"""
        if self.technical_requirements:
            # Исправлено: используем technical_requirements вместо technical_requests
            return [item.strip() for item in self.technical_requirements.split(',') if item.strip()]
        return []

    def get_tech_requirements_display(self):
        """Возвращает отображаемые названия выбранных технологий"""
        tech_dict = dict(TECH_CHOICES)
        selected_codes = self.get_tech_requirements_list()
        return [tech_dict.get(code, code) for code in selected_codes]
    
    def add_tech_requirement(self, tech_code):
        """Добавляет технологию к требованиям"""
        current_list = self.get_tech_requirements_list()
        if tech_code not in current_list:
            current_list.append(tech_code)
            self.technical_requirements = ', '.join(current_list)
    
    def remove_tech_requirement(self, tech_code):
        """Удаляет технологию из требований"""
        current_list = self.get_tech_requirements_list()
        if tech_code in current_list:
            current_list.remove(tech_code)
            self.technical_requirements = ', '.join(current_list)
    
    def has_tech_requirement(self, tech_code):
        """Проверяет, есть ли технология в требованиях"""
        return tech_code in self.get_tech_requirements_list()
    
    def clear_tech_requirements(self):
        """Очищает все технические требования"""
        self.technical_requirements = ""


class ServiceOrder(TimestampModel):
    STATUS_CHOICES = [
        ("new", _("Новый")),
        ("confirmed", _("Подтвержден")),
        ("in_progress", _("В работе")),
        ("completed", _("Выполнен")),
        ("cancelled", _("Отменен")),
    ]
    
    service = models.ForeignKey(
        Service,
        on_delete=models.PROTECT,
        verbose_name=_("Услуга"),
        related_name='orders'
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Пользователь"),
        related_name='service_orders'
    )
    
    full_name = models.CharField(
        max_length=255,
        verbose_name=_("ФИО")
    )
    
    phone = models.CharField(
        max_length=20,
        verbose_name=_("Телефон"),
        help_text=_("Формат: +7XXXXXXXXXX")
    )
    
    email = models.EmailField(
        verbose_name=_("Email"),
        max_length=255
    )
    
    message = models.TextField(
        verbose_name=_("Комментарий/Задача"),
        blank=True,
        help_text=_("Подробное описание того, что необходимо сделать")
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="new",
        verbose_name=_("Статус")
    )
    
    admin_notes = models.TextField(
        verbose_name=_("Заметки администратора"),
        blank=True,
        help_text=_("Внутренние заметки по заказу")
    )
    
    estimated_budget = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Предварительный бюджет"),
        help_text=_("Ориентировочная стоимость по мнению клиента")
    )
    
    deadline = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Желаемый срок выполнения"),
        help_text=_("Дата, к которой необходимо выполнить работу")
    )

    class Meta:
        verbose_name = _("Заказ услуги")
        verbose_name_plural = _("Заказы услуг")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['service', 'status']),
        ]

    def __str__(self):
        return f"Заказ #{self.pk} - {self.service.title}"

    def clean(self):
        """Валидация данных заказа"""
        super().clean()
        
        # Проверка формата телефона
        if self.phone:
            # Более гибкая проверка телефона
            phone_pattern = r'^[\+]?[1-9][\d\-\(\)\.]{9,15}$'
            if not re.match(phone_pattern, self.phone):
                raise ValidationError({
                    'phone': _('Неверный формат телефона. Используйте международный формат, например: +79991234567')
                })
        
        # Проверка бюджета
        if self.estimated_budget and self.estimated_budget < 0:
            raise ValidationError({'estimated_budget': _('Бюджет не может быть отрицательным.')})

    @property
    def short_id(self):
        """Короткий идентификатор заказа"""
        return f"SVC-{self.pk:06d}"

    def get_status_color(self):
        """Возвращает цвет для отображения статуса"""
        colors = {
            'new': 'blue',
            'confirmed': 'green',
            'in_progress': 'orange',
            'completed': 'purple',
            'cancelled': 'red',
        }
        return colors.get(self.status, 'gray')

    def get_contact_info(self):
        """Возвращает форматированную контактную информацию"""
        return f"{self.full_name}\n📞 {self.phone}\n✉️ {self.email}"
    
    def get_status_display_with_color(self):
        """Возвращает статус с HTML цветом"""
        from django.utils.html import format_html
        
        colors = {
            'new': '#3498db',      # синий
            'confirmed': '#2ecc71', # зеленый
            'in_progress': '#f39c12', # оранжевый
            'completed': '#9b59b6', # фиолетовый
            'cancelled': '#e74c3c', # красный
        }
        
        color = colors.get(self.status, '#95a5a6')
        status_display = self.get_status_display()
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            status_display
        )