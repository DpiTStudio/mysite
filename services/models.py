from django.db import models
from tinymce.models import HTMLField
from main.utils import RenameUploadTo
from main.models import ActiveModel, SEOModel, TimestampModel
from accounts.models import User

class Service(ActiveModel, SEOModel, TimestampModel):
    title = models.CharField(max_length=200, verbose_name="Название услуги")
    slug = models.SlugField(unique=True, verbose_name="URL")
    icon = models.FileField(upload_to=RenameUploadTo("services/icons/"), verbose_name="Иконка (SVG/PNG)", blank=True, null=True)
    
    short_description = models.TextField(verbose_name="Краткое описание", blank=True)
    description = HTMLField(verbose_name="Полное описание", default="<p>Описание услуги</p>")
    technical_requirements = HTMLField(verbose_name="Технические условия", blank=True, help_text="Языки, особенности и т.д.")
    
    PRICE_TYPE_CHOICES = [
        ('fixed', 'Фиксированная'),
        ('range', 'От и До'),
    ]
    price_type = models.CharField(max_length=10, choices=PRICE_TYPE_CHOICES, default='fixed', verbose_name="Тип цены")
    
    price_fixed = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Фиксированная цена")
    price_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Цена ОТ")
    price_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Цена ДО")
    
    currency = models.CharField(max_length=10, default="RUB", verbose_name="Валюта")
    
    order = models.IntegerField(default=0, verbose_name="Порядок сортировки")

    class Meta:
        verbose_name = "Услуга"
        verbose_name_plural = "Услуги"
        ordering = ["order", "title"]

    def __str__(self):
        return self.title

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
