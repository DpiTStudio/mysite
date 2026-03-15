from django.contrib import admin
from django.utils.html import format_html, format_html_join
from django.http import HttpResponse
import csv

from .models import Service, ServiceOrder, Technology, ServiceCategory, ServiceBenefit, ServiceStep, ServiceFAQ, ServicePricePlan



@admin.register(Technology)
class TechnologyAdmin(admin.ModelAdmin):
    search_fields = ('name',)

@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'order', 'is_active')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('order', 'is_active')
    search_fields = ('name', 'description')

class ServiceBenefitInline(admin.TabularInline):
    model = ServiceBenefit
    extra = 1

class ServiceStepInline(admin.TabularInline):
    model = ServiceStep
    extra = 1

class ServiceFAQInline(admin.TabularInline):
    model = ServiceFAQ
    extra = 1

class ServicePricePlanInline(admin.TabularInline):
    model = ServicePricePlan
    extra = 1



@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = (
        'title', 
        'category', 
        'price_display', 
        'is_active', 
        'is_popular', 
        'is_available_for_order', 
        'order'
    )
    list_filter = (
        'is_active', 
        'is_popular', 
        'is_available_for_order', 
        'price_type', 
        'category', 
        'complexity_level', 
        'technologies'
    )
    search_fields = (
        'title', 
        'description', 
        'short_description', 
        'technologies__name'
    )
    prepopulated_fields = {'slug': ('title',)}
    list_editable = (
        'is_active', 
        'is_popular', 
        'is_available_for_order', 
        'order'
    )
    filter_horizontal = ('technologies', 'related_portfolio')
    inlines = [ServiceBenefitInline, ServiceStepInline, ServiceFAQInline, ServicePricePlanInline]
    save_on_top = True

    save_as = True
    
    readonly_fields = ('get_tech_display', 'views')
    
    actions = ['make_active', 'make_inactive']
    
    fieldsets = (
        ('Основная информация', {
            'fields': (
                'title', 'slug', 'category', 'old_category_tag', 'icon', 
                'short_description', 'description', 'technologies', 'related_portfolio'
            )
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
                'order', 'is_active', 'is_popular', 'is_available_for_order', 'complexity_level',
                'meta_title', 'meta_description', 'meta_keywords', 'views'
            ),
            'classes': ('wide',),
        }),
        ('Выбранные технологии (только чтение)', {
            'fields': ('get_tech_display',),
            'classes': ('collapse',),
        }),
    )
    
    @admin.display(description='Цена', ordering='price_fixed')
    def price_display(self, obj):
        """Информативное отображение цены в списке"""
        return obj.get_price_display()
    
    @admin.display(description='Выбранные технологии')
    def get_tech_display(self, obj):
        """Красивое отображение выбранных технологий виде списка"""
        tech_list = obj.get_tech_requirements_display()
        if tech_list:
            items = format_html_join('', '<li>{}</li>', ((tech,) for tech in tech_list))
            return format_html('<ul style="margin: 0; padding-left: 20px;">{}</ul>', items)
        return "Технологии не выбраны"
    
    @admin.action(description="Активировать выбранные услуги")
    def make_active(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"Активировано услуг: {updated}")
    
    @admin.action(description="Деактивировать выбранные услуги")
    def make_inactive(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"Деактивировано услуг: {updated}")


@admin.register(ServiceOrder)
class ServiceOrderAdmin(admin.ModelAdmin):
    list_display = ('short_id', 'service', 'full_name', 'status_display', 'created_at', 'contact_info')
    list_filter = ('status', 'service', 'created_at')
    search_fields = ('full_name', 'email', 'phone', 'service__title', 'short_id')
    readonly_fields = ('created_at', 'updated_at', 'short_id')
    list_per_page = 25
    
    actions = ['mark_as_confirmed', 'mark_as_in_progress', 'mark_as_completed', 'export_to_csv']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('short_id', 'service', 'user', 'status')
        }),
        ('Контактные данные', {
            'fields': ('full_name', 'phone', 'email', 'message')
        }),
        ('Детали заказа', {
            'fields': ('estimated_budget', 'deadline', 'admin_notes'),
            'classes': ('wide',),
        }),
        ('Даты (Системные)', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    @admin.display(description='Статус', ordering='status')
    def status_display(self, obj):
        """Цветное отображение статуса в списке"""
        return obj.get_status_display_with_color()
    
    @admin.display(description='Контакты')
    def contact_info(self, obj):
        """Компактный вывод контактных данных"""
        return format_html(
            '<div style="white-space: nowrap;">'
            '📞 {}<br>✉️ <a href="mailto:{}">{}</a>'
            '</div>',
            obj.phone,
            obj.email,
            obj.email
        )
    
    @admin.action(description="Подтвердить выбранные заказы")
    def mark_as_confirmed(self, request, queryset):
        queryset.update(status='confirmed')
        self.message_user(request, "Статус обновлён: Подтвержден")
        
    @admin.action(description="Взять в работу выбранные заказы")
    def mark_as_in_progress(self, request, queryset):
        queryset.update(status='in_progress')
        self.message_user(request, "Статус обновлён: В работе")
    
    @admin.action(description="Отметить как выполненные")
    def mark_as_completed(self, request, queryset):
        queryset.update(status='completed')
        self.message_user(request, "Статус обновлён: Выполнен")

    @admin.action(description="Экспорт в CSV")
    def export_to_csv(self, request, queryset):
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]
        
        response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
        response['Content-Disposition'] = f'attachment; filename={meta.model_name}_export.csv'
        writer = csv.writer(response)
        
        writer.writerow(field_names)
        for obj in queryset:
            writer.writerow([getattr(obj, field) for field in field_names])
        
        return response