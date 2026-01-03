from django.db import models
from tinymce.models import HTMLField
from main.utils import RenameUploadTo
from main.models import ActiveModel, SEOModel, HeaderModel, TimestampModel


class PortfolioCategory(ActiveModel, SEOModel, HeaderModel):
    name = models.CharField(max_length=100, verbose_name="Название")
    slug = models.SlugField(unique=True, verbose_name="URL")
    logo = models.ImageField(upload_to=RenameUploadTo("portfolio/categories/"), verbose_name="Логотип")
    description = models.TextField(verbose_name="Описание")
    content = HTMLField(verbose_name="Описание на странице", default="<p>Описание</p>")
    order = models.IntegerField(default=0, verbose_name="Порядок")

    class Meta:
        verbose_name = "Категория портфолио"
        verbose_name_plural = "Категории портфолио"
        ordering = ["order", "name"]

    def __str__(self):
        return self.name


class Portfolio(ActiveModel, SEOModel, TimestampModel):
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    slug = models.SlugField(unique=True, verbose_name="URL")
    category = models.ForeignKey(
        PortfolioCategory, on_delete=models.CASCADE, verbose_name="Категория"
    )
    image = models.ImageField(upload_to=RenameUploadTo("portfolio/images/"), verbose_name="Изображение")
    content = HTMLField(verbose_name="Контент", default="<p>Контент сайта</p>")
    views = models.IntegerField(default=0, verbose_name="Просмотры")
    
    # New fields for service functionality
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Цена (обычная)")
    min_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Цена (минимальная)")
    max_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Цена (максимальная)")
    is_service = models.BooleanField(default=False, verbose_name="Это услуга")

    class Meta:
        verbose_name = "Портфолио/Услуга"
        verbose_name_plural = "Портфолио/Услуги"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def increment_views(self):
        self.views += 1
        Portfolio.objects.filter(pk=self.pk).update(views=self.views)


class ServiceOrder(TimestampModel):
    service = models.ForeignKey(Portfolio, on_delete=models.CASCADE, verbose_name="Услуга", limit_choices_to={'is_service': True})
    full_name = models.CharField(max_length=255, verbose_name="ФИО")
    email = models.EmailField(verbose_name="Email")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    message = models.TextField(verbose_name="Сообщение", blank=True, null=True)
    status = models.CharField(
        max_length=20,
        default="pending",
        choices=[
            ("pending", "Ожидает"),
            ("processing", "В обработке"),
            ("completed", "Завершено"),
            ("cancelled", "Отменено"),
        ],
        verbose_name="Статус"
    )

    class Meta:
        verbose_name = "Заказ услуги"
        verbose_name_plural = "Заказы услуг"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Заказ {self.service.title} от {self.full_name}"

