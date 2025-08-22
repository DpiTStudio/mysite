from django.db import models
from ckeditor.fields import RichTextField


class SiteSettings(models.Model):
    site_title = models.CharField(max_length=200, verbose_name="Название сайта")
    site_description = models.TextField(verbose_name="Описание сайта")
    meta_keywords = models.CharField(max_length=200, verbose_name="Ключевые слова")
    meta_description = models.CharField(max_length=255, verbose_name="Мета описание")
    logo = models.ImageField(upload_to="logos/", verbose_name="Логотип")
    favicon = models.ImageField(upload_to="favicons/", verbose_name="Фавикон")
    is_active = models.BooleanField(default=True, verbose_name="Активно")

    class Meta:
        verbose_name = "Настройки сайта"
        verbose_name_plural = "Настройки сайта"


class Page(models.Model):
    title = models.CharField(max_length=200, verbose_name="Заголовок страницы")
    slug = models.SlugField(unique=True, verbose_name="URL")
    content = RichTextField(verbose_name="Содержание")
    meta_title = models.CharField(max_length=200, verbose_name="Мета заголовок")
    meta_keywords = models.CharField(max_length=200, verbose_name="Ключевые слова")
    meta_description = models.CharField(max_length=255, verbose_name="Мета описание")
    show_in_menu = models.BooleanField(default=True, verbose_name="Показывать в меню")
    is_active = models.BooleanField(default=True, verbose_name="Активно")
    order = models.IntegerField(default=0, verbose_name="Порядок")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Страница"
        verbose_name_plural = "Страницы"
        ordering = ["order", "title"]

    def __str__(self):
        return self.title
