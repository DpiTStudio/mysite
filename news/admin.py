from django.contrib import admin
from django.utils.html import format_html
from .models import News, NewsCategory, DailyEvent
from .forms import NewsCategoryForm, NewsForm


class DailyEventInline(admin.TabularInline):
    """Inline для отображения событий дня в админке новостей"""
    model = DailyEvent
    extra = 0
    fields = ['event_type', 'title', 'description', 'image', 'order', 'created_at']
    readonly_fields = ['created_at']
    ordering = ['order', '-created_at']


class NewsCategoryAdmin(admin.ModelAdmin):
    form = NewsCategoryForm
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

    class Meta:
        verbose_name = "Категория новостей"
        verbose_name_plural = "Категории новостей"


class NewsAdmin(admin.ModelAdmin):
    form = NewsForm
    inlines = [DailyEventInline]
    list_display = [
        "title",
        "category",
        "news_date",
        "events_count",
        "is_active",
        "created_at",
        "views",
    ]
    list_editable = ["is_active"]
    prepopulated_fields = {"slug": ("title",)}
    list_filter = [
        "category",
        "is_active",
        "news_date",
        "created_at",
    ]
    search_fields = [
        "title",
        "content",
    ]
    date_hierarchy = "news_date"

    # Поля для отображения в админке
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "title",
                    "slug",
                    "category",
                    "news_date",
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

    def events_count(self, obj):
        """Отображает количество событий за день"""
        count = obj.get_events_count()
        return format_html(
            '<span style="color: {};">{} событий</span>',
            'green' if count > 0 else 'gray',
            count
        )
    events_count.short_description = "События"

    class Meta:
        verbose_name = "Новость"
        verbose_name_plural = "Новости"


class DailyEventAdmin(admin.ModelAdmin):
    """Админка для управления событиями дня"""
    list_display = [
        'title',
        'news',
        'event_type',
        'order',
        'created_at',
    ]
    list_filter = [
        'event_type',
        'news__category',
        'created_at',
    ]
    search_fields = [
        'title',
        'description',
        'news__title',
    ]
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        (
            "Основная информация",
            {
                "fields": (
                    "news",
                    "event_type",
                    "title",
                    "description",
                    "image",
                    "order",
                )
            },
        ),
        (
            "Связанный объект",
            {
                "fields": (
                    "related_object_type",
                    "related_object_id",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Временные метки",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                ),
                "classes": ("collapse",),
            },
        ),
    )
    date_hierarchy = "created_at"


admin.site.register(NewsCategory, NewsCategoryAdmin)
admin.site.register(News, NewsAdmin)
admin.site.register(DailyEvent, DailyEventAdmin)
