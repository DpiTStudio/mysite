from django.contrib import admin
from .models import Service, ServiceOrder

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('title', 'price_type', 'is_active', 'order')
    list_filter = ('is_active', 'price_type')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('order', 'is_active')

@admin.register(ServiceOrder)
class ServiceOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'service', 'full_name', 'status', 'created_at')
    list_filter = ('status', 'service', 'created_at')
    search_fields = ('full_name', 'email', 'phone', 'service__title')
    readonly_fields = ('created_at', 'updated_at')
