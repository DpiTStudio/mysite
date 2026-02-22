# knowledge_base/admin.py
"""
Этот файл настраивает интерфейс администратора Django для приложения базы знаний (knowledge_base).

Основные функции:
1. Регистрация модели Category (Категория):
   - Отображает поля: заголовок, порядок и иконку.
   - Автоматически генерирует 'slug' на основе заголовка.
   - Позволяет выполнять поиск по заголовку и сортирует записи по полю 'order'.

2. Регистрация модели Article (Статья):
   - Отображает поля: заголовок, категория, статус публикации, количество просмотров и дата создания.
   - Позволяет изменять статус публикации ('is_published') прямо в списке статей.
   - Предоставляет фильтры по категориям, статусу публикации и дате создания.
   - Автоматически генерирует 'slug' на основе заголовка.
   - Позволяет выполнять поиск по заголовку и содержимому статьи.
   - Сортирует статьи по дате создания (сначала новые).
"""


from django.contrib import admin
from .models import Category, Article

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'order', 'get_icon_admin')
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title',)
    ordering = ('order',)
    
    # мета класс
    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
    

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'is_published', 'views', 'created_at')
    list_editable = ('is_published',)
    list_filter = ('category', 'is_published', 'created_at')
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title', 'content')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    
    # оптимизация запросов
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('category')

    
    # мета класс
    class Meta:
        verbose_name = 'Статья'
        verbose_name_plural = 'Статьи'
