from django.contrib import admin
from django.utils.html import format_html
from django.contrib.admin.models import LogEntry
from .models import SiteSettings, Page


@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    list_display = [
        "action_time",
        "user",
        "content_type",
        "object_repr",
        "action_flag_display",
    ]
    list_filter = ["action_time", "user", "action_flag", "content_type"]
    search_fields = ["object_repr", "change_message"]
    date_hierarchy = "action_time"
    readonly_fields = [
        "action_time",
        "user",
        "content_type",
        "object_id",
        "object_repr",
        "action_flag",
        "change_message",
    ]

    def action_flag_display(self, obj):
        if obj.is_addition():
            return format_html('<span style="color: green;">Добавление</span>')
        elif obj.is_change():
            return format_html('<span style="color: blue;">Изменение</span>')
        elif obj.is_deletion():
            return format_html('<span style="color: red;">Удаление</span>')
        return "Неизвестно"

    action_flag_display.short_description = "Действие"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ["site_title", "is_active"]
    list_editable = ["is_active"]

    fieldsets = (
        (
            "Основная информация",
            {"fields": ("site_title", "site_slogan", "site_description", "site_domain", "is_active")},
        ),
        ("SEO настройки", {"fields": ("meta_keywords", "meta_description")}),
        ("Контент и медиа", {"fields": ("content", "fon_haeders", "logo", "favicon")}),
    )

    def has_delete_permission(self, request, obj=None):
        # Запрещаем удаление записей SiteSettings
        return False


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "slug",
        "show_in_menu",
        "is_active",
        "order",
        "logo_preview",
        "created_at",
    ]
    list_editable = ["show_in_menu", "is_active", "order"]
    list_filter = ["show_in_menu", "is_active", "created_at"]
    search_fields = ["title", "slug", "content"]
    prepopulated_fields = {"slug": ("title",)}

    fieldsets = (
        (
            "Основная информация",
            {"fields": ("title", "slug", "content", "order", "is_active")},
        ),
        (
            "Медиа и оформление",
            {
                "fields": ("logo", "fon_headers"),
                "description": "Логотип и фон шапки для этой страницы",
            },
        ),
        ("Настройки меню", {"fields": ("show_in_menu",)}),
        (
            "SEO настройки",
            {"fields": ("meta_title", "meta_keywords", "meta_description")},
        ),
    )

    def logo_preview(self, obj):
        if obj.logo:
            return format_html(
                '<img src="{}" style="width: 50px; height: auto;" />', obj.logo.url
            )
        return "Нет логотипа"

    logo_preview.short_description = "Превью лого"

    class Media:
        css = {
            "all": ("css/pages.css",),
        }

