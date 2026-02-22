import os
from io import BytesIO
from PIL import Image
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile

def optimize_image(image_field, max_size=(1920, 1080), quality=80):
    """
    Оптимизирует загруженное изображение: ресайзит и конвертирует в WebP.
    Использование в методе save() модели:
    if self.image:
        self.image = optimize_image(self.image)
    super().save(*args, **kwargs)
    """
    if not image_field:
        return image_field

    # Если файл уже есть на диске (начинается с пути медиа) и не in-memory (т.е. не только что загружен)
    # мы пропускаем оптимизацию, чтобы не сжимать повторно
    if not isinstance(image_field.file, InMemoryUploadedFile) and not hasattr(image_field.file, 'temporary_file_path'):
        # Если файл не загружен только что (не InMemory и не TemporaryUpload) - пропустить
        # Но иногда при обновлении файл тоже может быть объектом File. Лучший способ - проверить изменился ли хэш/наличие,
        # либо мы просто делаем это если имя файла не заканчивается на webp
        pass
    
    if image_field.name.lower().endswith('.webp'):
        return image_field

    try:
        # Открываем изображение с помощью Pillow
        img = Image.open(image_field)
        
        # Конвертируем в RGB если изображение имеет альфа-канал и мы хотим сохранить как JPEG,
        # но для WebP альфа-канал поддерживается, так что можно оставить RGBA.
        
        # Изменяем размер пропорционально
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # Создаем буфер для нового изображения
        output = BytesIO()
        
        # Сохраняем в формате WebP
        img.save(output, format='WEBP', quality=quality)
        output.seek(0)
        
        # Генерируем новое имя файла
        name = os.path.splitext(image_field.name)[0]
        new_name = f"{name}.webp"
        
        # Создаем новый объект ContentFile
        new_image = InMemoryUploadedFile(
            ContentFile(output.read()),
            'ImageField',
            new_name,
            'image/webp',
            output.tell(),
            None
        )
        return new_image
    except Exception as e:
        print(f"Error optimizing image: {e}")
        return image_field
