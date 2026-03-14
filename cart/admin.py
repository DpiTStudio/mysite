from django.contrib import admin
from .models import Order, OrderItem, PromoCode, PromoCodeUsage


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['service', 'portfolio']
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'first_name', 'last_name', 'email', 'phone', 'paid', 'status', 'created', 'updated']
    list_filter = ['paid', 'status', 'created', 'updated']
    search_fields = ['first_name', 'last_name', 'email', 'phone']
    inlines = [OrderItemInline]


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
