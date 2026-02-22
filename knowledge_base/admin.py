from django.contrib import admin
from .models import Category, Article

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'order', 'icon')
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title',)

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'is_published', 'views', 'created_at')
    list_editable = ('is_published',)
    list_filter = ('category', 'is_published', 'created_at')
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title', 'content')
