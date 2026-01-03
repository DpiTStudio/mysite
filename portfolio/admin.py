from django.contrib import admin
from .models import Portfolio, PortfolioCategory, ServiceOrder
from .forms import PortfolioCategoryForm, PortfolioForm


class PortfolioCategoryAdmin(admin.ModelAdmin):
    form = PortfolioCategoryForm
    list_display = [
        "name",
        "is_active",
        "order",
    ]
    list_editable = [
        "order",
        "is_active",
    ]
    fieldsets = (
        (
            "Основная информация",
            {
                "fields": (
                    "name",
                    "slug",
                    "logo",
                    "description",
                    "content",
                    "order",
                    "is_active",
                )
            },
        ),
        (
            "Настройка шапки (Header)",
            {
                "fields": (
                    "header_image",
                    "header_title",
                    "header_description",
                ),
                "description": "Эти настройки позволяют переопределить шапку сайта для данной категории.",
            },
        ),
        (
            "SEO настройки",
            {"fields": ("meta_title", "meta_keywords"), "classes": ("collapse",)},
        ),
    )
    prepopulated_fields = {"slug": ("name",)}
    list_filter = ["is_active"]
    search_fields = ["name"]


class PortfolioAdmin(admin.ModelAdmin):
    form = PortfolioForm
    list_display = [
        "title",
        "category",
        "price",
        "min_price",
        "max_price",
        "is_service",
        "is_active",
        "created_at",
        "views",
    ]
    list_editable = ["is_active", "price", "min_price", "max_price", "is_service"]
    prepopulated_fields = {"slug": ("title",)}
    list_filter = [
        "is_service",
        "category",
        "is_active",
        "created_at",
    ]
    search_fields = [
        "title",
        "content",
    ]
    date_hierarchy = "created_at"

    # Поля для отображения в админке
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "title",
                    "slug",
                    "category",
                    "image",
                    "content",
                    "price",
                    "min_price",
                    "max_price",
                    "is_service",
                    "views",
                )
            },
        ),
        (
            "SEO настройки",
            {
                "fields": (
                    "meta_title",
                    "meta_keywords",
                    "meta_description",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Дополнительно",
            {
                "fields": ("is_active",),
                "classes": ("collapse",),
            },
        ),
    )


@admin.register(ServiceOrder)
class ServiceOrderAdmin(admin.ModelAdmin):
    list_display = ["service", "full_name", "email", "phone", "status", "created_at"]
    list_filter = ["status", "created_at", "service"]
    search_fields = ["full_name", "email", "phone", "message"]
    list_editable = ["status"]
    readonly_fields = ["created_at", "updated_at"]
    fieldsets = (
        ("Информация о заказе", {"fields": ("service", "status")}),
        ("Контактные данные", {"fields": ("full_name", "email", "phone", "message")}),
        ("Системная информация", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )


admin.site.register(PortfolioCategory, PortfolioCategoryAdmin)
admin.site.register(Portfolio, PortfolioAdmin)

