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
    prepopulated_fields = {"slug": ("name",)}
    list_filter = ["is_active"]
    search_fields = ["name"]

    class Meta:
        verbose_name = "Категория портфолио"
        verbose_name_plural = "Категории портфолио"


class PortfolioAdmin(admin.ModelAdmin):
    form = PortfolioForm
    list_display = [
        "title",
        "category",
        "is_active",
        "created_at",
        "views",
    ]
    list_editable = ["is_active"]
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

    class Meta:
        verbose_name = "Портфолио"
        verbose_name_plural = "Портфолио"


admin.site.register(PortfolioCategory, PortfolioCategoryAdmin)
admin.site.register(Portfolio, PortfolioAdmin)
