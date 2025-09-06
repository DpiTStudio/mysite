"""
Утилиты для приложения main
"""
from django.core.cache import cache
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.utils.text import slugify
from django.utils.html import strip_tags
from django.conf import settings
import re


class CacheMixin:
    """Миксин для работы с кэшем"""
    
    cache_timeout = 3600  # 1 час по умолчанию
    
    def get_cache_key(self, *args, **kwargs):
        """Генерирует ключ кэша"""
        return f"{self.__class__.__name__}_{hash(str(args) + str(kwargs))}"
    
    def get_from_cache(self, cache_key):
        """Получает данные из кэша"""
        return cache.get(cache_key)
    
    def set_to_cache(self, cache_key, data, timeout=None):
        """Сохраняет данные в кэш"""
        timeout = timeout or self.cache_timeout
        cache.set(cache_key, data, timeout)
    
    def clear_cache(self, pattern=None):
        """Очищает кэш"""
        if pattern:
            cache.delete_many(cache.keys(pattern))
        else:
            cache.clear()


class SEOHelper:
    """Помощник для SEO оптимизации"""
    
    @staticmethod
    def generate_meta_title(title, site_name=None, max_length=60):
        """Генерирует мета-заголовок"""
        if site_name and len(title) + len(site_name) + 3 <= max_length:
            return f"{title} | {site_name}"
        return title[:max_length]
    
    @staticmethod
    def generate_meta_description(content, max_length=160):
        """Генерирует мета-описание из контента"""
        # Удаляем HTML теги
        text = strip_tags(content)
        # Удаляем лишние пробелы
        text = re.sub(r'\s+', ' ', text).strip()
        # Обрезаем до нужной длины
        if len(text) <= max_length:
            return text
        return text[:max_length-3] + "..."
    
    @staticmethod
    def generate_keywords(content, title, max_keywords=10):
        """Генерирует ключевые слова из контента и заголовка"""
        # Объединяем заголовок и контент
        text = f"{title} {content}"
        # Удаляем HTML теги
        text = strip_tags(text)
        # Приводим к нижнему регистру
        text = text.lower()
        # Удаляем знаки препинания
        text = re.sub(r'[^\w\s]', ' ', text)
        # Разбиваем на слова
        words = text.split()
        # Фильтруем короткие слова
        words = [word for word in words if len(word) > 3]
        # Подсчитываем частоту
        word_count = {}
        for word in words:
            word_count[word] = word_count.get(word, 0) + 1
        # Сортируем по частоте
        sorted_words = sorted(word_count.items(), key=lambda x: x[1], reverse=True)
        # Возвращаем топ ключевых слов
        return [word for word, count in sorted_words[:max_keywords]]


class PaginationHelper:
    """Помощник для пагинации"""
    
    @staticmethod
    def paginate_queryset(queryset, page_number, per_page=20):
        """Создает пагинацию для queryset"""
        paginator = Paginator(queryset, per_page)
        try:
            page_obj = paginator.page(page_number)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)
        return page_obj
    
    @staticmethod
    def get_pagination_context(page_obj, page_range=5):
        """Создает контекст для пагинации"""
        current_page = page_obj.number
        total_pages = page_obj.paginator.num_pages
        
        # Вычисляем диапазон страниц для отображения
        start_page = max(1, current_page - page_range // 2)
        end_page = min(total_pages, start_page + page_range - 1)
        
        if end_page - start_page < page_range - 1:
            start_page = max(1, end_page - page_range + 1)
        
        return {
            'page_obj': page_obj,
            'current_page': current_page,
            'total_pages': total_pages,
            'has_previous': page_obj.has_previous(),
            'has_next': page_obj.has_next(),
            'previous_page_number': page_obj.previous_page_number() if page_obj.has_previous() else None,
            'next_page_number': page_obj.next_page_number() if page_obj.has_next() else None,
            'page_range': range(start_page, end_page + 1),
            'show_first': start_page > 1,
            'show_last': end_page < total_pages,
        }


class SearchHelper:
    """Помощник для поиска"""
    
    @staticmethod
    def build_search_query(query, fields):
        """Строит поисковый запрос для нескольких полей"""
        if not query or not fields:
            return Q()
        
        q_objects = Q()
        for field in fields:
            q_objects |= Q(**{f"{field}__icontains": query})
        
        return q_objects
    
    @staticmethod
    def highlight_search_terms(text, query, max_length=200):
        """Подсвечивает найденные термины в тексте"""
        if not query or not text:
            return text
        
        # Обрезаем текст до нужной длины
        if len(text) > max_length:
            text = text[:max_length] + "..."
        
        # Подсвечиваем найденные термины
        highlighted_text = re.sub(
            f'({re.escape(query)})',
            r'<mark>\1</mark>',
            text,
            flags=re.IGNORECASE
        )
        
        return highlighted_text


class ImageHelper:
    """Помощник для работы с изображениями"""
    
    @staticmethod
    def get_image_dimensions(image_field):
        """Получает размеры изображения"""
        try:
            if image_field and hasattr(image_field, 'width') and hasattr(image_field, 'height'):
                return image_field.width, image_field.height
        except (ValueError, OSError):
            pass
        return None, None
    
    @staticmethod
    def is_image_landscape(image_field):
        """Проверяет, является ли изображение горизонтальным"""
        width, height = ImageHelper.get_image_dimensions(image_field)
        if width and height:
            return width > height
        return False
    
    @staticmethod
    def get_image_alt_text(image_field, default_text="Изображение"):
        """Генерирует alt текст для изображения"""
        if hasattr(image_field, 'name') and image_field.name:
            # Извлекаем имя файла без расширения
            filename = image_field.name.split('/')[-1].split('.')[0]
            return filename.replace('_', ' ').replace('-', ' ').title()
        return default_text


class URLHelper:
    """Помощник для работы с URL"""
    
    @staticmethod
    def clean_url_path(path):
        """Очищает путь URL от лишних символов"""
        # Удаляем начальный и конечный слеш
        path = path.strip('/')
        # Заменяем множественные слеши на одинарные
        path = re.sub(r'/+', '/', path)
        return path
    
    @staticmethod
    def build_absolute_url(request, relative_url):
        """Строит абсолютный URL"""
        if request:
            return request.build_absolute_uri(relative_url)
        return relative_url
    
    @staticmethod
    def is_valid_slug(slug):
        """Проверяет валидность slug"""
        if not slug:
            return False
        # Проверяем, что slug содержит только буквы, цифры, дефисы и подчеркивания
        return bool(re.match(r'^[a-zA-Z0-9_-]+$', slug))


class ValidationHelper:
    """Помощник для валидации"""
    
    @staticmethod
    def validate_phone(phone):
        """Валидирует номер телефона"""
        if not phone:
            return False
        # Удаляем все символы кроме цифр и +
        clean_phone = re.sub(r'[^\d+]', '', phone)
        # Проверяем формат
        return bool(re.match(r'^\+?[1-9]\d{1,14}$', clean_phone))
    
    @staticmethod
    def validate_email(email):
        """Валидирует email"""
        if not email:
            return False
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def sanitize_html(html_content):
        """Очищает HTML контент от потенциально опасных тегов"""
        # Список разрешенных тегов
        allowed_tags = [
            'p', 'br', 'strong', 'em', 'u', 'b', 'i', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
            'ul', 'ol', 'li', 'a', 'img', 'div', 'span', 'blockquote', 'pre', 'code'
        ]
        
        # Простая очистка - в реальном проекте лучше использовать библиотеку bleach
        for tag in ['script', 'style', 'iframe', 'object', 'embed']:
            html_content = re.sub(f'<{tag}[^>]*>.*?</{tag}>', '', html_content, flags=re.IGNORECASE | re.DOTALL)
            html_content = re.sub(f'<{tag}[^>]*/?>', '', html_content, flags=re.IGNORECASE)
        
        return html_content


class PerformanceHelper:
    """Помощник для оптимизации производительности"""
    
    @staticmethod
    def optimize_queryset(queryset, select_related=None, prefetch_related=None):
        """Оптимизирует queryset для уменьшения количества запросов"""
        if select_related:
            queryset = queryset.select_related(*select_related)
        if prefetch_related:
            queryset = queryset.prefetch_related(*prefetch_related)
        return queryset
    
    @staticmethod
    def get_cache_key_for_queryset(queryset, prefix="queryset"):
        """Генерирует ключ кэша для queryset"""
        # Создаем хэш из SQL запроса и параметров
        sql_hash = hash(str(queryset.query))
        return f"{prefix}_{sql_hash}"
    
    @staticmethod
    def chunk_queryset(queryset, chunk_size=1000):
        """Разбивает queryset на чанки для обработки больших объемов данных"""
        total = queryset.count()
        for start in range(0, total, chunk_size):
            end = min(start + chunk_size, total)
            yield queryset[start:end]
