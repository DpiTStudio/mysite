from django.contrib import admin
from .models import Ticket, TicketMessage


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ("id", "subject", "user", "status", "priority", "created_at", "updated_at")
    list_filter = ("status", "priority", "created_at")
    search_fields = ("subject", "description", "user__username", "user__email")
    readonly_fields = ("created_at", "updated_at", "closed_at")
    date_hierarchy = "created_at"
    
    fieldsets = (
        ("Основная информация", {
            "fields": ("user", "subject", "description")
        }),
        ("Статус и приоритет", {
            "fields": ("status", "priority")
        }),
        ("Даты", {
            "fields": ("created_at", "updated_at", "closed_at")
        }),
    )


@admin.register(TicketMessage)
class TicketMessageAdmin(admin.ModelAdmin):
    list_display = ("id", "ticket", "user", "created_at", "is_internal")
    list_filter = ("is_internal", "created_at")
    search_fields = ("message", "ticket__subject", "user__username")
    readonly_fields = ("created_at",)
    date_hierarchy = "created_at"
