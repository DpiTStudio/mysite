from django.db import models
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.utils.text import slugify
from tinymce.models import HTMLField


class TimeStampedModel(models.Model):
    """Абстрактная модель с временными метками"""
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        abstract = True


class SEOFields(models.Model):
    """Абстрактная модель с SEO полями"""
    meta_title = models.CharField(
        max_length=200, 
        verbose_name="Мета заголовок",
        validators=[MinLengthValidator(10), MaxLengthValidator(200)]
    )
    meta_keywords = models.CharField(
        max_length=200, 
        verbose_name="Ключевые слова",
        validators=[MaxLengthValidator(200)]
    )
    meta_description = models.CharField(
        max_length=255, 
        verbose_name="Мета описание",
        validators=[MinLengthValidator(50), MaxLengthValidator(255)]
    )

    class Meta:
        abstract = True


class ActiveModel(models.Model):
    """Абстрактная модель с полем активности"""
    is_active = models.BooleanField(default=True, verbose_name="Активно")

    class Meta:
        abstract = True


class OrderableModel(models.Model):
    """Абстрактная модель с полем порядка"""
    order = models.IntegerField(default=0, verbose_name="Порядок")

    class Meta:
        abstract = True


class SiteSettings(TimeStampedModel, SEOFields, ActiveModel):
    """Настройки сайта"""
    site_title = models.CharField(
        max_length=200, 
        verbose_name="Название сайта",
        validators=[MinLengthValidator(3), MaxLengthValidator(200)]
    )
    site_description = models.TextField(
        verbose_name="Описание сайта",
        validators=[MinLengthValidator(10)]
    )
    content = HTMLField(verbose_name="Контент", default="<p>Контент сайта</p>")
    logo = models.ImageField(
        upload_to="logos/", 
        verbose_name="Логотип",
        help_text="Рекомендуемый размер: 200x60px"
    )
    favicon = models.ImageField(
        upload_to="favicons/", 
        verbose_name="Фавикон",
        help_text="Рекомендуемый размер: 32x32px"
    )
    phone = models.CharField(
        max_length=20, 
        verbose_name="Телефон",
        blank=True,
        null=True
    )
    email = models.EmailField(
        verbose_name="Email",
        blank=True,
        null=True
    )
    address = models.TextField(
        verbose_name="Адрес",
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = "Настройки сайта"
        verbose_name_plural = "Настройки сайта"

    def __str__(self):
        return self.site_title

    def save(self, *args, **kwargs):
        # Обеспечиваем, что есть только одна запись настроек
        if not self.pk and SiteSettings.objects.exists():
            raise ValueError("Может существовать только одна запись настроек сайта")
        super().save(*args, **kwargs)


class Page(TimeStampedModel, SEOFields, ActiveModel, OrderableModel):
    """Модель страницы"""
    title = models.CharField(
        max_length=200, 
        verbose_name="Заголовок страницы",
        validators=[MinLengthValidator(3), MaxLengthValidator(200)]
    )
    slug = models.SlugField(
        unique=True, 
        verbose_name="URL",
        help_text="URL страницы (например: about-us)"
    )
    content = HTMLField(verbose_name="Контент", default="<p>Контент страницы</p>")
    show_in_menu = models.BooleanField(default=True, verbose_name="Показывать в меню")
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Родительская страница",
        related_name="children"
    )
    template = models.CharField(
        max_length=100,
        default="main/page_detail.html",
        verbose_name="Шаблон",
        help_text="Путь к шаблону страницы"
    )

    class Meta:
        verbose_name = "Страница"
        verbose_name_plural = "Страницы"
        ordering = ["order", "title"]
        unique_together = ['slug', 'parent']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Автоматически создаем slug из title, если не указан
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        """Возвращает абсолютный URL страницы"""
        from django.urls import reverse
        return reverse('page_detail', kwargs={'slug': self.slug})

    def get_breadcrumbs(self):
        """Возвращает хлебные крошки для страницы"""
        breadcrumbs = []
        current = self
        while current:
            breadcrumbs.insert(0, current)
            current = current.parent
        return breadcrumbs

    @property
    def is_root(self):
        """Проверяет, является ли страница корневой"""
        return self.parent is None

    @property
    def has_children(self):
        """Проверяет, есть ли у страницы дочерние страницы"""
        return self.children.filter(is_active=True).exists()
