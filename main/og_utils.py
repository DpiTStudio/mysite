from django.http import HttpResponse
from PIL import Image, ImageDraw, ImageFont
import os
from django.conf import settings
from django.core.cache import cache
import hashlib

def generate_og_image(request):
    """
    Генерирует динамическое изображение для Open Graph.
    Параметры: title, subtitle, color, theme.
    """
    title = request.GET.get('title', 'DPIT-CMS')
    subtitle = request.GET.get('subtitle', 'Современная система управления контентом')
    theme = request.GET.get('theme', 'dark') # dark, light, season
    
    # Кеширование по хешу параметров
    cache_key = f"og_image_{hashlib.md5((title + subtitle + theme).encode()).hexdigest()}"
    cached_img = cache.get(cache_key)
    if cached_img:
        return HttpResponse(cached_img, content_type="image/png")

    # Создаем изображение 1200x630 (стандарт OG)
    width, height = 1200, 630
    if theme == 'dark':
        bg_color = (20, 20, 25)
        text_color = (255, 255, 255)
        accent_color = (52, 152, 219)
    else:
        bg_color = (245, 245, 250)
        text_color = (40, 40, 50)
        accent_color = (41, 128, 185)

    img = Image.new('RGB', (width, height), color=bg_color)
    draw = ImageDraw.Draw(img)
    
    # Рисуем градиент или узоры (упрощенно - линии)
    for i in range(0, width, 40):
        draw.line([(i, 0), (i+200, height)], fill=(accent_color[0], accent_color[1], accent_color[2], 30), width=1)

    # Загрузка шрифта (попытка найти системный или использовать дефолтный)
    try:
        # Пытаемся найти шрифт в папке статики (если он там есть)
        font_path = os.path.join(settings.STATIC_ROOT, 'fonts/Inter-Bold.ttf')
        if not os.path.exists(font_path):
             font_path = "arial.ttf" # Fallback для Windows
        
        font_title = ImageFont.truetype(font_path, 80)
        font_sub = ImageFont.truetype(font_path, 40)
    except Exception:
        font_title = ImageFont.load_default()
        font_sub = ImageFont.load_default()

    # Рисуем текст
    draw.text((80, 200), title, font=font_title, fill=text_color)
    draw.text((80, 320), subtitle, font=font_sub, fill=(text_color[0], text_color[1], text_color[2], 180))
    
    # Рисуем маркер бренда
    draw.rectangle([80, 180, 200, 190], fill=accent_color)

    # Сохраняем в память
    from io import BytesIO
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    img_data = buffer.getvalue()
    
    cache.set(cache_key, img_data, 60*60*24) # 24 часа
    
    return HttpResponse(img_data, content_type="image/png")
