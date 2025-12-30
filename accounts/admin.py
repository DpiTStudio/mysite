from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("username", "email", "phone", "first_name", "last_name", "is_staff", "created_at")
    list_filter = ("is_staff", "is_superuser", "is_active", "created_at")
    search_fields = ("username", "email", "phone", "first_name", "last_name")
    readonly_fields = ("created_at", "updated_at", "date_joined", "last_login")
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Дополнительная информация", {
            "fields": ("phone", "avatar", "created_at", "updated_at")
        }),
    )
