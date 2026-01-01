from django.contrib import admin
from .models import Review

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('full_name', 'content', 'email')
    list_editable = ('status',)
