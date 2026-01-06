from django.db import models
from tinymce.models import HTMLField
from main.utils import RenameUploadTo
from main.models import ActiveModel, SEOModel, TimestampModel
from accounts.models import User

# Константы для выбора технологий
TECH_CHOICES = [
    ('html', 'HTML/CSS'),
    ('js', 'JavaScript'),
    ('python', 'Python'),
    ('java', 'Java'),
    ('php', 'PHP'),
    ('react', 'React'),
    ('vue', 'Vue.js'),
    ('angular', 'Angular'),
    ('mobile', 'Мобильная версия'),
    ('adaptive', 'Адаптивный дизайн'),
    ('seo', 'SEO-оптимизация'),
]

class Service(ActiveModel, SEOModel, TimestampModel):
    title = models.CharField(
                max_length=200, 
                verbose_name="Название услуги")
    slug = models.SlugField(
                unique=True, 
                verbose_name="URL")
    icon = models.FileField(
                upload_to=RenameUploadTo("services/icons/"), 
                verbose_name="Иконка (JPG/GIF/PNG)", 
                blank=True, 
                null=True)
    short_description = models.TextField(
                verbose_name="Краткое описание", 
                blank=True)
    description = HTMLField(
                verbose_name="Полное описание", 
                default="<p>Описание услуги</p>")
    technical_requirements = models.TextField(
        verbose_name="Технические условия",
        blank=True,
        help_text="Выбранные значения сохраняются через запятую"
    )
    
    PRICE_TYPE_CHOICES = [
        ('fixed', 'Фиксированная'),
        ('range', 'От и До'),
    ]
    price_type = models.CharField(
                max_length=10, 
                choices=PRICE_TYPE_CHOICES, 
                default='fixed', 
                verbose_name="Тип цены")
    
    price_fixed = models.DecimalField(
                max_digits=10, 
                decimal_places=2, 
                null=True, blank=True, 
                verbose_name="Фиксированная цена")
    price_min = models.DecimalField(
                max_digits=10, 
                decimal_places=2, 
                null=True, 
                blank=True, 
                verbose_name="Цена ОТ")
    price_max = models.DecimalField(
                max_digits=10, 
                decimal_places=2, 
                null=True, 
                blank=True, 
                verbose_name="Цена ДО")
    currency = models.CharField(
                max_length=10, 
                default="RUB", 
                verbose_name="Валюта")
    order = models.IntegerField(
                default=0, 
                verbose_name="Порядок сортировки")

    class Meta:
        verbose_name = "Услуга"
        verbose_name_plural = "Услуги"
        ordering = ["order", "title"]

    def __str__(self):
        return self.title

    def get_tech_requirements_list(self):
        """Возвращает список выбранных технологий"""
        if self.technical_requirements:
            return [item.strip() for item in self.technical_requirements.split(',') if item.strip()]
        return []

    def get_tech_requirements_display(self):
        """Возвращает отображаемые названия выбранных технологий"""
        tech_dict = dict(TECH_CHOICES)
        return [tech_dict.get(code, code) for code in self.get_tech_requirements_list()]


class ServiceOrder(TimestampModel):
    STATUS_CHOICES = [
        ("new", "Новый"),
        ("processing", "В обработке"),
        ("completed", "Выполнен"),
        ("cancelled", "Отменен"),
    ]
    
    service = models.ForeignKey(Service, on_delete=models.CASCADE, verbose_name="Услуга", related_name='orders')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Пользователь", related_name='service_orders')
    
    full_name = models.CharField(max_length=255, verbose_name="ФИО")
    phone = models.CharField(max_length=50, verbose_name="Телефон")
    email = models.EmailField(verbose_name="Email")
    
    message = models.TextField(verbose_name="Комментарий", blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="new", verbose_name="Статус")
    
    class Meta:
        verbose_name = "Заказ услуги"
        verbose_name_plural = "Заказы услуг"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Заказ {self.pk} - {self.service.title}"