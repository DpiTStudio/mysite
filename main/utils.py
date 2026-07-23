"""
Модуль utils.py приложения main

Этот файл содержит вспомогательные утилиты для работы с файлами и строками.
Основное назначение - автоматическое переименование загружаемых файлов с транслитерацией
и добавлением временной метки для предотвращения конфликтов имен.
"""

# Импорт модуля для работы с операционной системой (пути, файлы)
import os
# Импорт модуля для работы с датой и временем
import datetime
# Импорт функции slugify для преобразования строк в URL-friendly формат
from django.utils.text import slugify
# Импорт декоратора для сериализации классов (необходимо для миграций Django)
from django.utils.deconstruct import deconstructible


def transliterate(string):
    """
    Функция транслитерации кириллицы в латиницу.
    
    Преобразует русские буквы в их латинские эквиваленты согласно стандартной схеме
    транслитерации. Используется для генерации имен файлов из русских названий.
    
    Примеры:
        "Привет" -> "Privet"
        "Новости" -> "Novosti"
        "Портфолио" -> "Portfolio"
    
    Args:
        string (str): Строка с кириллическими символами
    
    Returns:
        str: Строка с латинскими символами
    
    Note:
        Функция обрабатывает как заглавные, так и строчные буквы.
        Специальные символы (Ъ, Ь) удаляются.
    """
    # Словарь соответствия заглавных русских букв латинским
    capital_letters = {
        'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'E', 
        'Ж': 'Zh', 'З': 'Z', 'И': 'I', 'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M', 
        'Н': 'N', 'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U', 
        'Ф': 'F', 'Х': 'Kh', 'Ц': 'Ts', 'Ч': 'Ch', 'Ш': 'Sh', 'Щ': 'Shch',
        'Ъ': '', 'Ы': 'Y', 'Ь': '', 'Э': 'E', 'Ю': 'Yu', 'Я': 'Ya'
    }
    
    # Словарь соответствия строчных русских букв латинским
    lower_case_letters = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'e', 
        'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm', 
        'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u', 
        'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'shch',
        'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya'
    }
    
    # Замена заглавных букв
    for cyrillic, latin in capital_letters.items():
        string = string.replace(cyrillic, latin)
    
    # Замена строчных букв
    for cyrillic, latin in lower_case_letters.items():
        string = string.replace(cyrillic, latin)
    
    return string


@deconstructible
class RenameUploadTo:
    """
    Класс для динамического переименования загружаемых файлов.
    
    Используется в полях ImageField и FileField модели Django для автоматического
    переименования файлов при загрузке. Формат имени файла: title_дата-время.расширение
    
    Преимущества:
    - Предотвращает конфликты имен файлов
    - Делает имена файлов читаемыми и понятными
    - Добавляет временную метку для отслеживания
    - Транслитерирует русские названия в латиницу
    
    Пример использования:
        avatar = models.ImageField(upload_to=RenameUploadTo("avatars/"))
        # Файл "фото.jpg" будет сохранен как "avatars/foto_2023-01-15_14-30-45.jpg"
    
    Note:
        Декоратор @deconstructible необходим для корректной работы миграций Django,
        так как позволяет сериализовать класс для сохранения в миграциях.
    """
    
    def __init__(self, path):
        """
        Инициализация класса.
        
        Args:
            path (str): Базовый путь для сохранения файлов (например, "avatars/", "logos/")
        """
        # Сохранение базового пути для использования при генерации полного пути
        self.base_path = path

    def __call__(self, instance, filename):
        """
        Метод вызывается Django при загрузке файла.
        
        Генерирует новое имя файла на основе:
        - Названия объекта (title, name и т.д.)
        - Текущей даты и времени
        - Оригинального расширения файла
        
        Args:
            instance: Экземпляр модели, к которому привязан файл
            filename (str): Оригинальное имя загружаемого файла
        
        Returns:
            str: Полный путь к файлу относительно MEDIA_ROOT
                Формат: "base_path/transliterated_title_YYYY-MM-DD_HH-MM-SS.ext"
        """
        # Извлечение расширения файла (последняя часть после точки)
        # Например, из "photo.jpg" получим "jpg"
        ext = filename.split('.')[-1]
        
        # Поиск значимого названия в объекте для формирования имени файла
        # Проверяем стандартные атрибуты моделей
        title = ""
        for attr in ['title', 'name', 'site_title', 'username']:
            # Проверка наличия атрибута у объекта
            if hasattr(instance, attr):
                # Получение значения атрибута
                val = getattr(instance, attr)
                # Если значение не пустое, используем его
                if val:
                    title = str(val)
                    break
        
        # Если не нашли название в самом объекте, проверяем связанные объекты
        # Это полезно для случаев, когда файл привязан к связанной модели
        # (например, аватар пользователя в профиле, резервная копия лога)
        if not title:
            # Список возможных атрибутов для связанных объектов
            for rel_attr in ['user', 'log_file', 'news', 'portfolio']:
                # Проверка наличия связи
                if hasattr(instance, rel_attr):
                    # Получение связанного объекта
                    related = getattr(instance, rel_attr)
                    if related:
                        # Поиск названия в связанном объекте
                        for attr in ['username', 'title', 'name']:
                            if hasattr(related, attr):
                                val = getattr(related, attr)
                                if val:
                                    title = str(val)
                                    break
                    # Если нашли название, прекращаем поиск
                    if title:
                        break

        # Если название так и не найдено, используем значение по умолчанию
        if not title:
            title = "file"
            
        # Транслитерация названия из кириллицы в латиницу
        # Например, "Новости" -> "Novosti"
        title = transliterate(title)
        
        # Преобразование в slug (URL-friendly формат)
        # slugify делает строку безопасной для использования в URL:
        # - Удаляет специальные символы
        # - Заменяет пробелы на дефисы
        # - Приводит к нижнему регистру
        # Например, "Hello World!" -> "hello-world"
        title_slug = slugify(title)
        
        # Если после slugify получилась пустая строка, используем значение по умолчанию
        if not title_slug:
            title_slug = "file"
            
        # Получение текущей даты и времени в формате YYYY-MM-DD_HH-MM-SS
        # Это предотвращает конфликты имен при загрузке файлов с одинаковыми названиями
        date_str = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        
        # Формирование нового имени файла
        # Формат: transliterated_title_YYYY-MM-DD_HH-MM-SS.ext
        # Пример: "novosti_2023-01-15_14-30-45.jpg"
        new_filename = f"{title_slug}_{date_str}.{ext}"
        
        # Объединение базового пути и нового имени файла
        # os.path.join корректно обрабатывает разделители путей для разных ОС
        # Результат: "avatars/novosti_2023-01-15_14-30-45.jpg"
        return os.path.join(self.base_path, new_filename)


def optimize_image(image_field, max_width=1920, max_height=1080, quality=85):
    """
    Оптимизирует изображение: изменяет размер, если он превышает допустимый, 
    и сжимает его в формат WebP для высокой скорости загрузки.
    
    Args:
        image_field: Поле модели ImageField / FileField
        max_width (int): Максимальная ширина
        max_height (int): Максимальная высота
        quality (int): Качество сжатия WebP (1-100)
    """
    if not image_field or not hasattr(image_field, 'path') or not os.path.exists(image_field.path):
        return

    try:
        from PIL import Image
        
        filepath = image_field.path
        ext = os.path.splitext(filepath)[1].lower()
        
        # Пропускаем SVG и GIF (с анимацией)
        if ext in ['.svg', '.gif']:
            return
            
        with Image.open(filepath) as img:
            # Конвертируем в RGB если файл в RGBA/P и без альфа-канала
            if img.mode in ('P', 'RGBA'):
                img = img.convert('RGB')
                
            # Изменение размера с сохранением пропорций
            img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            
            # Сохранение в оптимизированный WebP или JPEG
            if ext != '.webp':
                webp_filepath = os.path.splitext(filepath)[0] + '.webp'
                img.save(webp_filepath, 'WEBP', quality=quality, optimize=True)
                
                # Если исходный файл не webp, можем обновить путь или оставить как оптимизированный webp
                if os.path.exists(filepath) and filepath != webp_filepath:
                    os.remove(filepath)
            else:
                img.save(filepath, 'WEBP', quality=quality, optimize=True)
    except Exception:
        # В случае ошибки Pillow (например, не картинка) игнорируем без падения
        pass


def validate_file_upload(file_obj, max_size_mb=10, allowed_extensions=None):
    """
    Валидатор для загружаемых файлов по размеру и расширению.
    """
    from django.core.exceptions import ValidationError

    if allowed_extensions is None:
        allowed_extensions = ['jpg', 'jpeg', 'png', 'webp', 'svg', 'gif', 'pdf', 'doc', 'docx', 'zip']

    # Проверка размера
    if file_obj.size > max_size_mb * 1024 * 1024:
        raise ValidationError(f"Размер файла не должен превышать {max_size_mb} МБ.")

    # Проверка расширения
    ext = os.path.splitext(file_obj.name)[1][1:].lower()
    if ext not in allowed_extensions:
        raise ValidationError(f"Недопустимый формат файла .{ext}. Разрешенные: {', '.join(allowed_extensions)}")

