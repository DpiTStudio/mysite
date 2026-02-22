from django.db import models
from django.urls import reverse
from tinymce.models import HTMLField

class Category(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название")
    slug = models.SlugField(max_length=200, unique=True, verbose_name="URL")
    icon = models.CharField(max_length=50, blank=True, null=True, verbose_name="Иконка (FontAwesome)", help_text="Например: fas fa-book")
    order = models.IntegerField(default=0, verbose_name="Порядок сортировки")

    class Meta:
        verbose_name = "Категория БД"
        verbose_name_plural = "Категории БД"
        ordering = ['order', 'title']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('knowledge_base:category', kwargs={'slug': self.slug})

class Article(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='articles', verbose_name="Категория")
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    slug = models.SlugField(max_length=200, unique=True, verbose_name="URL")
    content = HTMLField(verbose_name="Содержание")
    views = models.PositiveIntegerField(default=0, verbose_name="Просмотры")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")
    is_published = models.BooleanField(default=True, verbose_name="Опубликовано")

    class Meta:
        verbose_name = "Статья"
        verbose_name_plural = "Статьи"
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('knowledge_base:article', kwargs={'slug': self.slug})
