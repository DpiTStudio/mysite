# admin.py - Улучшенная версия
from django.contrib import admin
from django.utils.html import format_html
from .models import Service, ServiceOrder
from .forms import ServiceAdminForm

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    form = ServiceAdminForm
    list_display = ('title', 'category', 'price_display', 'is_active', 'order')
    list_filter = ('is_active', 'price_type', 'category', 'complexity_level')
    search_fields = ('title', 'description', 'short_description', 'technical_requirements')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('is_active', 'order')
    save_on_top = True
    save_as = True
    
    # Поля только для чтения в форме редактирования
    readonly_fields = ('get_tech_display',)
    
    # Группировка действий
    actions = ['make_active', 'make_inactive']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'slug', 'category', 'icon', 'short_description', 'description', 'technical_requirements')
        }),
        ('Что получит клиент', {
            'fields': ('deliverables', 'estimated_time'),
            'classes': ('collapse', 'wide'),
        }),
        ('Ценообразование', {
            'fields': ('price_type', 'price_fixed', 'price_min', 'price_max', 'currency'),
            'classes': ('wide',),
        }),
        ('Настройки и SEO', {
            'fields': (
                'order', 
                'is_active', 
                'is_popular',
                'complexity_level',
                'meta_title', 
                'meta_description', 
                'meta_keywords'
            ),
            'classes': ('wide',),
        }),
        ('Выбранные технологии (только чтение)', {
            'fields': ('get_tech_display',),
            'classes': ('collapse',),
        }),
    )
    
    def price_display(self, obj):
        """Кастомное отображение цены в списке"""
        return obj.get_price_display()
    price_display.short_description = 'Цена'
    price_display.admin_order_field = 'price_fixed'
    
    def get_tech_display(self, obj):
        """Отображение выбранных технологий в админке"""
        tech_list = obj.get_tech_requirements_display()
        if tech_list:
            return format_html(
                '<ul style="margin: 0; padding-left: 20px;">{}</ul>',
                ''.join([f'<li>{tech}</li>' for tech in tech_list])
            )
        return "Технологии не выбраны"
    get_tech_display.short_description = 'Выбранные технологии'
    
    # Действия администратора
    def make_active(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, "Выбранные услуги активированы")
    make_active.short_description = "Активировать выбранные услуги"
    
    def make_inactive(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, "Выбранные услуги деактивированы")
    make_inactive.short_description = "Деактивировать выбранные услуги"


@admin.register(ServiceOrder)
class ServiceOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'service', 'full_name', 'status_display', 'created_at', 'contact_info')
    list_filter = ('status', 'service', 'created_at')
    search_fields = ('full_name', 'email', 'phone', 'service__title')
    readonly_fields = ('created_at', 'updated_at', 'short_id')
    list_per_page = 25
    
    # Экспорт действий
    actions = ['mark_as_confirmed', 'mark_as_completed', 'export_to_csv']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('short_id', 'service', 'user', 'status')
        }),
        ('Контактные данные', {
            'fields': ('full_name', 'phone', 'email', 'message')
        }),
        ('Детали заказа', {
            'fields': ('estimated_budget', 'deadline', 'admin_notes'),
            'classes': ('collapse',),
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    def status_display(self, obj):
        """Цветное отображение статуса в списке"""
        return obj.get_status_display_with_color()
    status_display.short_description = 'Статус'
    status_display.allow_tags = True
    
    def contact_info(self, obj):
        """Контактная информация в компактном виде"""
        return format_html(
            '📞 {}<br>✉️ {}',
            obj.phone,
            obj.email
        )
    contact_info.short_description = 'Контакты'
    
    # Действия администратора
    def mark_as_confirmed(self, request, queryset):
        queryset.update(status='confirmed')
        self.message_user(request, "Выбранные заказы подтверждены")
    mark_as_confirmed.short_description = "Подтвердить выбранные заказы"
    
    def mark_as_completed(self, request, queryset):
        queryset.update(status='completed')
        self.message_user(request, "Выбранные заказы отмечены как выполненные")
    mark_as_completed.short_description = "Отметить как выполненные"

    def export_to_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse
        
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename={meta}.csv'
        writer = csv.writer(response)
        
        writer.writerow(field_names)
        for obj in queryset:
            writer.writerow([getattr(obj, field) for field in field_names])
        
        return response
    export_to_csv.short_description = "Экспорт в CSV"