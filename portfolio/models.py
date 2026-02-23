from django.db import models
from django.urls import reverse
from tinymce.models import HTMLField
from main.utils import RenameUploadTo
from main.models import ActiveModel, SEOModel, HeaderModel, TimestampModel


class PortfolioCategory(ActiveModel, SEOModel, HeaderModel):
    """
    Модель категории портфолио.
    Позволяет группировать работы по типам (например, 'Веб-сайты', 'Дизайн').
    """
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

    def get_absolute_url(self):
        """Возвращает URL страницы категории"""
        return reverse("portfolio:by_category", kwargs={"category_slug": self.slug})


class Portfolio(ActiveModel, SEOModel, TimestampModel):
    """
    Модель работы (кейса) в портфолио.
    Представляет выполненный проект с описанием, изображениями и SEO данными.
    """
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    slug = models.SlugField(unique=True, verbose_name="URL")
    category = models.ForeignKey(
        PortfolioCategory, on_delete=models.CASCADE, verbose_name="Категория"
    )
    image = models.ImageField(upload_to=RenameUploadTo("portfolio/images/"), verbose_name="Изображение")
    content = HTMLField(verbose_name="Контент", default="<p>Контент сайта</p>")
    views = models.IntegerField(default=0, verbose_name="Просмотры")
    
    # Для интеграции с корзиной
    is_available_for_order = models.BooleanField(default=False, verbose_name="Доступно для заказа")
    price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name="Цена (Оформление)")


    class Meta:
        verbose_name = "Портфолио"
        verbose_name_plural = "Портфолио"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        """Возвращает URL детальной страницы работы"""
        return reverse("portfolio:detail", kwargs={"slug": self.slug})

    def increment_views(self):
        """Увеличивает счетчик просмотров работы"""
        self.views += 1
        Portfolio.objects.filter(pk=self.pk).update(views=self.views)




