from django.contrib import admin
from .models import Portfolio, PortfolioCategory
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
        "is_active",
        "is_available_for_order",
        "price",
        "created_at",
        "views",
    ]
    list_editable = ["is_active", "is_available_for_order", "price"]
    prepopulated_fields = {"slug": ("title",)}
    list_filter = [
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
                    "is_available_for_order",
                    "price",
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


admin.site.register(PortfolioCategory, PortfolioCategoryAdmin)
admin.site.register(Portfolio, PortfolioAdmin)
