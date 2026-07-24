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
        'icon_preview',
        'title', 
        'category', 
        'price_display', 
        'stats_badges',
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
                ('title', 'slug'),
                ('category', 'old_category_tag'),
                'icon', 
                'short_description', 
                'description', 
                'technologies', 
                'related_portfolio'
            )
        }),
        ('Что получит клиент', {
            'fields': (
                ('complexity_level', 'estimated_time'),
                'deliverables'
            ),
            'classes': ('collapse', 'wide'),
        }),
        ('Ценообразование', {
            'fields': (
                ('price_type', 'currency'),
                ('price_fixed', 'price_min', 'price_max')
            ),
            'classes': ('wide',),
        }),
        ('Настройки и SEO', {
            'fields': (
                ('order', 'views'),
                ('is_active', 'is_popular', 'is_available_for_order'),
                'meta_title', 'meta_description', 'meta_keywords'
            ),
            'classes': ('wide',),
        }),
        ('Выбранные технологии (только чтение)', {
            'fields': ('get_tech_display',),
            'classes': ('collapse',),
        }),
    )
    
    @admin.display(description='Иконка')
    def icon_preview(self, obj):
        if obj.icon:
            return format_html('<img src="{}" style="height: 28px; width: 28px; object-fit: contain; border-radius: 6px; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); padding: 2px;" />', obj.icon.url)
        return format_html('<span style="color: var(--text-muted); font-size: 14px;">—</span>')

    @admin.display(description='Инфо (кол-во)')
    def stats_badges(self, obj):
        benefits = obj.benefits.count()
        steps = obj.steps.count()
        faqs = obj.faqs.count()
        plans = obj.price_plans.count()
        
        return format_html(
            '<div class="admin-stats-badges" style="display: flex; gap: 4px; font-weight: 600;">'
            '<span class="badge badge-info" title="Преимущества" style="background: rgba(14,165,233,0.15) !important; color: #0ea5e9 !important; border: 1px solid rgba(14,165,233,0.3);"><i class="fas fa-gift"></i> {}</span>'
            '<span class="badge badge-warning" title="Этапы" style="background: rgba(245,158,11,0.15) !important; color: #f59e0b !important; border: 1px solid rgba(245,158,11,0.3);"><i class="fas fa-arrow-right"></i> {}</span>'
            '<span class="badge badge-danger" title="FAQ" style="background: rgba(239,68,68,0.15) !important; color: #ef4444 !important; border: 1px solid rgba(239,68,68,0.3);"><i class="fas fa-question"></i> {}</span>'
            '<span class="badge badge-success" title="Тарифы" style="background: rgba(16,185,129,0.15) !important; color: #10b981 !important; border: 1px solid rgba(16,185,129,0.3);"><i class="fas fa-tags"></i> {}</span>'
            '</div>',
            benefits, steps, faqs, plans
        )

    @admin.display(description='Цена', ordering='price_fixed')
    def price_display(self, obj):
        """Информативное отображение цены в списке"""
        currency_symbols = {'RUB': '₽', 'USD': '$', 'EUR': '€', 'KZT': '₸'}
        symbol = currency_symbols.get(obj.currency, obj.currency)
        
        if obj.price_type == 'fixed' and obj.price_fixed:
            formatted = f"{obj.price_fixed:,.0f}".replace(',', ' ')
            return format_html('<span class="price-tag fixed" style="background: rgba(99,102,241,0.15); color: #818cf8; border: 1px solid rgba(99,102,241,0.3); padding: 2px 6px; border-radius: 4px; font-weight: bold; font-size: 12px; white-space: nowrap;">{} {}</span>', formatted, symbol)
        
        elif obj.price_type == 'range' and obj.price_min and obj.price_max:
            min_fmt = f"{obj.price_min:,.0f}".replace(',', ' ')
            max_fmt = f"{obj.price_max:,.0f}".replace(',', ' ')
            return format_html('<span class="price-tag range" style="background: rgba(14,165,233,0.15); color: #38bdf8; border: 1px solid rgba(14,165,233,0.3); padding: 2px 6px; border-radius: 4px; font-weight: bold; font-size: 12px; white-space: nowrap;">{} - {} {}</span>', min_fmt, max_fmt, symbol)
            
        elif obj.price_type == 'contact':
            return format_html('<span class="price-tag contact" style="background: rgba(245,158,11,0.15); color: #fbbf24; border: 1px solid rgba(245,158,11,0.3); padding: 2px 6px; border-radius: 4px; font-weight: bold; font-size: 12px; white-space: nowrap;">Договорная</span>')
            
        return format_html('<span class="price-tag contact" style="background: rgba(148,163,184,0.15); color: #cbd5e1; border: 1px solid rgba(148,163,184,0.3); padding: 2px 6px; border-radius: 4px; font-weight: bold; font-size: 12px; white-space: nowrap;">Уточняйте</span>')
    
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