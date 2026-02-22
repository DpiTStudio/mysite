from django.db import models
from django.urls import reverse
from django.utils.html import format_html
from tinymce.models import HTMLField


def upload_to_category(instance, filename):
    return f'category_icons/{filename}'

class Category(models.Model):
    # основные поля
    title = models.CharField(max_length=200, verbose_name="Название")
    slug = models.SlugField(max_length=200, unique=True, verbose_name="URL")
    # Иконка
    icon_img = models.ImageField(upload_to=upload_to_category, blank=True, null=True, verbose_name="Иконка")
    # Содержание
    content = HTMLField(verbose_name="Содержание")
    # Дата и время
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")
    # Статус
    is_published = models.BooleanField(default=True, verbose_name="Опубликовано")
    views = models.PositiveIntegerField(default=0, verbose_name="Просмотры")
    # Порядок
    order = models.IntegerField(default=0, verbose_name="Порядок сортировки")

    class Meta:
        verbose_name = "Категория БД"
        verbose_name_plural = "Категории БД"
        ordering = ['order', 'title']

    def __str__(self):
        return self.title
    
    def get_icon(self):
        if self.icon_img:
            return self.icon_img.url
        return None
    
    def get_icon_admin(self):
        if self.icon_img:
            return format_html('<img src="{}" width="50" height="50" />', self.icon_img.url)
        return None
    get_icon_admin.short_description = 'Иконка'
    get_icon_admin.allow_tags = True
    
    def get_content(self):
        return self.content
    get_content.short_description = 'Содержание'
    get_content.allow_tags = True   

    def get_absolute_url(self):
        return reverse('knowledge_base:category', kwargs={'slug': self.slug})

class Article(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='articles', verbose_name="Категория")
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    slug = models.SlugField(max_length=200, unique=True, verbose_name="URL")
    # Содержание
    content = HTMLField(verbose_name="Содержание")
    # Просмотры
    views = models.PositiveIntegerField(default=0, verbose_name="Просмотры")
    # Дата и время
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")
    # Статус
    is_published = models.BooleanField(default=True, verbose_name="Опубликовано")

    class Meta:
        verbose_name = "Статья"
        verbose_name_plural = "Статьи"
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('knowledge_base:article', kwargs={'slug': self.slug})
