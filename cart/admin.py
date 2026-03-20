from django.contrib import admin
from django.utils.html import format_html
from .models import Order, OrderItem, PromoCode, PromoCodeUsage


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['service', 'portfolio']
    extra = 0
    readonly_fields = ['get_item_title', 'get_price_display', 'get_cost']
    fields = ['service', 'portfolio', 'price_type', 'price', 'price_min', 'price_max', 'quantity', 'get_cost']

    def get_item_title(self, obj):
        return obj.get_item_title()
    get_item_title.short_description = "Название"

    def get_cost(self, obj):
        return f"{obj.get_cost()} ₽"
    get_cost.short_description = "Сумма"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'full_name_display', 'email', 'phone',
        'status_badge', 'paid', 'promo_badge',
        'auto_registered', 'user', 'created'
    ]
    list_filter = ['paid', 'status', 'auto_registered', 'created', 'updated']
    search_fields = ['first_name', 'last_name', 'email', 'phone', 'promo_code_applied']
    readonly_fields = ['created', 'updated', 'get_total_cost', 'get_final_cost', 'auto_registered']
    inlines = [OrderItemInline]
    date_hierarchy = 'created'
    list_per_page = 25

    fieldsets = (
        ("Клиент", {
            'fields': ('user', 'auto_registered', 'first_name', 'last_name', 'email', 'phone', 'company')
        }),
        ("Заказ", {
            'fields': ('status', 'paid', 'comment', 'get_total_cost', 'get_final_cost')
        }),
        ("Скидка / Промокод", {
            'fields': ('promo_code_applied', 'discount_amount'),
            'classes': ('collapse',),
        }),
        ("Даты", {
            'fields': ('created', 'updated'),
            'classes': ('collapse',),
        }),
    )

    def full_name_display(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or "—"
    full_name_display.short_description = "Клиент"

    def status_badge(self, obj):
        colors = {
            'new': '#0d6efd',
            'confirmed': '#6f42c1',
            'in_progress': '#fd7e14',
            'completed': '#198754',
            'cancelled': '#dc3545',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background:{};color:#fff;padding:3px 8px;border-radius:4px;font-size:12px">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = "Статус"

    def promo_badge(self, obj):
        if obj.promo_code_applied:
            return format_html(
                '<span style="color:#198754;font-weight:bold">✓ {}</span> <small style="color:#6c757d">−{} ₽</small>',
                obj.promo_code_applied, obj.discount_amount
            )
        return "—"
    promo_badge.short_description = "Промокод"

    def get_total_cost(self, obj):
        return f"{obj.get_total_cost()} ₽"
    get_total_cost.short_description = "Сумма заказа (до скидки)"

    def get_final_cost(self, obj):
        return f"{obj.get_final_cost()} ₽"
    get_final_cost.short_description = "Итого (со скидкой)"


@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = [
        'code', 'discount_type', 'discount_value',
        'valid_from', 'valid_until',
        'max_uses', 'current_uses', 'is_active', 'created_at'
    ]
    list_filter = ['is_active', 'discount_type']
    search_fields = ['code']
    readonly_fields = ['current_uses', 'created_at']
    list_editable = ['is_active']

    def get_readonly_fields(self, request, obj=None):
        if obj:  # При редактировании code не изменяем
            return self.readonly_fields + ['code']
        return self.readonly_fields


@admin.register(PromoCodeUsage)
class PromoCodeUsageAdmin(admin.ModelAdmin):
    list_display = ['promo_code', 'order', 'user', 'discount_amount', 'used_at']
    list_filter = ['promo_code', 'used_at']
    search_fields = ['promo_code__code', 'order__id']
    readonly_fields = ['promo_code', 'order', 'user', 'discount_amount', 'used_at']
