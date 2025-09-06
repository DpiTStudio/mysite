from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import SiteSettings, Page


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    """Админка для настроек сайта"""

    list_display = ["site_title", "phone", "email", "is_active", "created_at"]
    list_editable = ["is_active"]
    list_filter = ["is_active", "created_at"]
    search_fields = ["site_title", "phone", "email"]
    readonly_fields = ["created_at", "updated_at"]

    fieldsets = (
        (
            "Основная информация",
            {"fields": ("site_title", "site_description", "content", "is_active")},
        ),
        (
            "SEO",
            {
                "fields": ("meta_title", "meta_keywords", "meta_description"),
                "classes": ("collapse",),
            },
        ),
        ("Медиа", {"fields": ("logo", "favicon"), "classes": ("collapse",)}),
        (
            "Контакты",
            {"fields": ("phone", "email", "address"), "classes": ("collapse",)},
        ),
        (
            "Временные метки",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def has_add_permission(self, request):
        # Разрешаем добавление только если нет записей
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # Запрещаем удаление настроек сайта
        return False


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    """Админка для страниц"""

    list_display = [
        "title",
        "slug",
        "parent",
        "show_in_menu",
        "is_active",
        "order",
        "created_at",
    ]
    list_editable = ["show_in_menu", "is_active", "order"]
    list_filter = ["is_active", "show_in_menu", "parent", "created_at"]
    search_fields = ["title", "slug", "meta_title", "content"]
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ["created_at", "updated_at"]
    list_per_page = 25

    fieldsets = (
        ("Основная информация", {"fields": ("title", "slug", "content", "template")}),
        ("Навигация", {"fields": ("parent", "show_in_menu", "order")}),
        (
            "SEO",
            {
                "fields": ("meta_title", "meta_keywords", "meta_description"),
                "classes": ("collapse",),
            },
        ),
        ("Статус", {"fields": ("is_active",)}),
        (
            "Временные метки",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def get_queryset(self, request):
        """Оптимизируем запросы"""
        return super().get_queryset(request).select_related("parent")

    def get_form(self, request, obj=None, **kwargs):
        """Исключаем страницу из списка возможных родителей"""
        form = super().get_form(request, obj, **kwargs)
        if obj and obj.pk:
            # Исключаем текущую страницу и её потомков из списка родителей
            form.base_fields["parent"].queryset = Page.objects.exclude(
                pk__in=obj.get_descendants(include_self=True).values_list(
                    "pk", flat=True
                )
            )
        return form

    def get_descendants(self, obj):
        """Получает всех потомков страницы"""
        if not obj:
            return Page.objects.none()
        descendants = []
        children = obj.children.all()
        for child in children:
            descendants.append(child)
            descendants.extend(self.get_descendants(child))
        return descendants

    def save_model(self, request, obj, form, change):
        """Дополнительная логика при сохранении"""
        if not change:  # Если создаем новую страницу
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    actions = ["make_active", "make_inactive", "show_in_menu", "hide_from_menu"]

    def make_active(self, request, queryset):
        """Активировать выбранные страницы"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f"Активировано {updated} страниц.")

    def make_inactive(self, request, queryset):
        """Деактивировать выбранные страницы"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f"Деактивировано {updated} страниц.")

    def show_in_menu(self, request, queryset):
        """Показать в меню выбранные страницы"""
        updated = queryset.update(show_in_menu=True)
        self.message_user(request, f"Показано в меню {updated} страниц.")

    def hide_from_menu(self, request, queryset):
        """Скрыть из меню выбранные страницы"""
        updated = queryset.update(show_in_menu=False)
        self.message_user(request, f"Скрыто из меню {updated} страниц.")

    make_active.short_description = "Активировать выбранные страницы"
    make_inactive.short_description = "Деактивировать выбранные страницы"
    show_in_menu.short_description = "Показать в меню"
    hide_from_menu.short_description = "Скрыть из меню"
