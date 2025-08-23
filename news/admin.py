from django.contrib import admin
from tinymce.models import HTMLField
from .models import News


class NewsCategoryAdmin(admin.ModelAdmin):
    list_display = ["title", "is_active"]
    list_editable = ["is_active"]
    prepopulated_fields = {"slug": ("title",)}

    class Meta:
        verbose_name = "Категория новостей"
        verbose_name_plural = "Категории новостей"
        ordering = ["order", "name"]


class NewsAdmin(admin.ModelAdmin):
    list_display = ["title", "slug", "category", "is_active"]
    list_editable = ["is_active"]
    prepopulated_fields = {"slug": ("title",)}

    class Meta:
        verbose_name = "Новость"
        verbose_name_plural = "Новости"
        ordering = ["-created_at"]


admin.site.register(News, NewsAdmin)
