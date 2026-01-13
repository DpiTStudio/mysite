from django.contrib import admin
from django.utils.html import format_html
from django.contrib.admin.models import LogEntry
from .models import SiteSettings, Page, AnalyticsScript


# ... (LogEntryAdmin)

@admin.register(AnalyticsScript)
class AnalyticsScriptAdmin(admin.ModelAdmin):
    list_display = ["name", "position", "is_active"]
    list_editable = ["position", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["name", "script_code"]


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

    def get_fieldsets(self, request, obj=None):
        return (
            (
                "Основная информация",
                {"fields": ("site_title", 
                            "site_slogan", 
                            "site_description", 
                            "site_domain", 
                            "is_active")
                },
            ),
            (
                "SEO настройки", 
                {"fields": ("meta_title", 
                            "meta_keywords", 
                            "meta_description")
                }
            ),
            (
                "Контент и медиа", 
                {"fields": ("content", 
                            "fon_haeders", 
                            "logo", 
                            "favicon")
                }
            ),
            (
                "Соц-сети: VK", 
                {"fields": ("site_vk", 
                            "site_vk_img")}
            ),
            (
                "Соц-сети: OK", 
                {"fields": ("site_ok", 
                            "site_ok_img")}
            ),
            (
                "Соц-сети: Facebook", 
                {"fields": ("site_facebook", 
                            "site_facebook_img")}
            ),
            (
                "Соц-сети: LinkedIn", 
                {"fields": ("site_linkedin", 
                            "site_linkedin_img")}
            ),
            (
                "Соц-сети: Instagram", 
                {"fields": ("site_instagram", 
                            "site_instagram_img")}
            ),
            (
                "Соц-сети: Twitter", 
                {"fields": ("site_twitter", 
                            "site_twitter_img")}
            ),
            (
                "Соц-сети: Telegram", 
                {"fields": ("site_telegram", 
                            "site_telegram_img")}
            ),
            (
                "Соц-сети: WhatsApp", 
                {"fields": ("site_whatsapp", 
                            "site_whatsapp_img")}
            ),
            (
                "Соц-сети: YouTube", 
                {"fields": ("site_youtube", 
                            "site_youtube_img")}
            ),
            (
                "Контакты", {"fields": ("site_address", 
                                        "site_phone_1", 
                                        "site_phone_2", 
                                        "site_email")
                            }
            ),
            ("Время работы", {"fields": ("site_work_time",)}),
        )

    def has_delete_permission(self, request, obj=None):
        # Запрещаем удаление записей SiteSettings
        return False
    
    def has_add_permission(self, request):
        # Запрещаем добавление записей SiteSettings
        return False

    # Добавляем превью для изображений соцсетей в списке
    def social_img_preview(self, obj, field_name):
        image = getattr(obj, field_name, None)
        if image:
            return format_html(
                '<img src="{}" style="width: 30px; height: 30px; object-fit: contain;" />', 
                image.url
            )
        return format_html('<span style="color: #999;">нет иконки</span>')

    def vk_img_preview(self, obj):
        return self.social_img_preview(obj, 'site_vk_img')
    
    def ok_img_preview(self, obj):
        return self.social_img_preview(obj, 'site_ok_img')
    
    def facebook_img_preview(self, obj):
        return self.social_img_preview(obj, 'site_facebook_img')
    
    def linkedin_img_preview(self, obj):
        return self.social_img_preview(obj, 'site_linkedin_img')
    
    def instagram_img_preview(self, obj):
        return self.social_img_preview(obj, 'site_instagram_img')
    
    def twitter_img_preview(self, obj):
        return self.social_img_preview(obj, 'site_twitter_img')
    
    def telegram_img_preview(self, obj):
        return self.social_img_preview(obj, 'site_telegram_img')
    
    def whatsapp_img_preview(self, obj):
        return self.social_img_preview(obj, 'site_whatsapp_img')
    
    def youtube_img_preview(self, obj):
        return self.social_img_preview(obj, 'site_youtube_img')

    # Опционально: добавляем в list_display превью иконок
    list_display = ["site_title", "is_active", "vk_img_preview", "telegram_img_preview"]


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