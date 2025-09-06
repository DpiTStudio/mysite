from django.contrib import admin
from .models import SiteSettings, Page


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ["site_title", "is_active"]
    list_editable = ["is_active"]


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ["title", "slug", "show_in_menu", "is_active", "order"]
    list_editable = ["show_in_menu", "is_active", "order"]
    prepopulated_fields = {"slug": ("title",)}
