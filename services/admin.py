from django.contrib import admin
from .models import Service, ServiceOrder
from .forms import ServiceAdminForm

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    form = ServiceAdminForm
    list_display = ('title', 'price_fixed', 'price_min', 'price_max','is_active', 'order')
    list_filter = ('is_active', 'price_type')
    # search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('price_fixed', 'price_min', 'price_max', 'is_active', 'order')
    save_on_top = True
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'slug', 'icon', 'short_description', 'description', 'technical_requirements')
    
        }),
        ('Цена', {
            'fields': ('price_type', 'price_fixed', 'price_min', 'price_max', 'currency'),
            'classes': ('wide',)
        }),
        ('Настройки', {
            'fields': ('order', 'is_active')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords'),
            'classes': ('collapse',)
        }),
    )

@admin.register(ServiceOrder)
class ServiceOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'service', 'full_name', 'status', 'created_at')
    list_filter = ('status', 'service', 'created_at')
    search_fields = ('full_name', 'email', 'phone', 'service__title')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('service', 'user', 'status')
        }),
        ('Контактные данные', {
            'fields': ('full_name', 'phone', 'email', 'message')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )