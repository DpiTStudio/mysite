import os
import datetime
from django.utils.text import slugify
from django.utils.deconstruct import deconstructible

def transliterate(string):
    """
    Простая транслитерация кириллицы в латиницу.
    """
    capital_letters = {
        'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'E', 'Ж': 'Zh', 'З': 'Z',
        'И': 'I', 'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M', 'Н': 'N', 'О': 'O', 'П': 'P', 'Р': 'R',
        'С': 'S', 'Т': 'T', 'У': 'U', 'Ф': 'F', 'Х': 'Kh', 'Ц': 'Ts', 'Ч': 'Ch', 'Ш': 'Sh', 'Щ': 'Shch',
        'Ъ': '', 'Ы': 'Y', 'Ь': '', 'Э': 'E', 'Ю': 'Yu', 'Я': 'Ya'
    }
    lower_case_letters = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'e', 'ж': 'zh', 'з': 'z',
        'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r',
        'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'shch',
        'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya'
    }
    for cyrillic, latin in capital_letters.items():
        string = string.replace(cyrillic, latin)
    for cyrillic, latin in lower_case_letters.items():
        string = string.replace(cyrillic, latin)
    return string

@deconstructible
class RenameUploadTo:
    """
    Класс для динамического переименования загружаемых файлов.
    Формат: title_дата-загрузки.расширение
    """
    def __init__(self, path):
        self.base_path = path

    def __call__(self, instance, filename):
        ext = filename.split('.')[-1]
        
        # Пытаемся найти заголовок или имя в объекте
        title = ""
        for attr in ['title', 'name', 'site_title', 'username']:
            if hasattr(instance, attr):
                val = getattr(instance, attr)
                if val:
                    title = str(val)
                    break
        
        # Если не нашли, проверяем связанные объекты (например, для резервных копий или профилей)
        if not title:
            for rel_attr in ['user', 'log_file', 'news', 'portfolio']:
                if hasattr(instance, rel_attr):
                    related = getattr(instance, rel_attr)
                    if related:
                        for attr in ['username', 'title', 'name']:
                            if hasattr(related, attr):
                                val = getattr(related, attr)
                                if val:
                                    title = str(val)
                                    break
                    if title:
                        break

        if not title:
            title = "file"
            
        # Транслитерация и слаг
        title = transliterate(title)
        title_slug = slugify(title)
        
        if not title_slug:
            title_slug = "file"
            
        # Текущая дата и время
        date_str = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        
        # Новое имя файла
        new_filename = f"{title_slug}_{date_str}.{ext}"
        
        return os.path.join(self.base_path, new_filename)
