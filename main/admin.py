from django.contrib import admin
from .models import SiteSettings, Page


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ["site_title", "is_active"]
    list_editable = ["is_active"]

    fieldsets = (
        ('Основная информация', {
            'fields': ('site_title', 'site_slogan', 'site_description', 'is_active')
        }),
        ('SEO настройки', {
            'fields': ('meta_keywords', 'meta_description')
        }),
        ('Контент и медиа', {
            'fields': ('content', 'logo', 'favicon')
        }),
    )

    def has_delete_permission(self, request, obj=None):
        # Запрещаем удаление записей SiteSettings
        return False


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ["title", "slug", "show_in_menu", "is_active", "order", "created_at"]
    list_editable = ["show_in_menu", "is_active", "order"]
    list_filter = ["show_in_menu", "is_active", "created_at"]
    search_fields = ["title", "slug", "content"]
    prepopulated_fields = {"slug": ("title",)}

    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'slug', 'content', 'order', 'is_active')
        }),
        ('Настройки меню', {
            'fields': ('show_in_menu',)
        }),
        ('SEO настройки', {
            'fields': ('meta_title', 'meta_keywords', 'meta_description')
        }),
    )