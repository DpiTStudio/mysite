from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import slugify
from django.utils import timezone

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

def get_unique_slug(model_class, title):
    base_slug = slugify(transliterate(title))
    if not base_slug:
        base_slug = "news-item"
    slug = base_slug
    num = 1
    while model_class.objects.filter(slug=slug).exists():
        slug = f"{base_slug}-{num}"
        num += 1
    return slug

@receiver(post_save)
def auto_create_news(sender, instance, created, **kwargs):
    # Избегаем рекурсии, если сохраняется сама новость
    from news.models import News, NewsCategory
    if sender == News or sender == NewsCategory:
        return

    # Импортируем модели внутри функций
    from portfolio.models import Portfolio
    from reviews.models import Review
    from main.models import Page
    
    if sender == Portfolio:
        if instance.is_active:
            category_name = instance.category.name
            news_category, _ = NewsCategory.objects.get_or_create(
                name=category_name,
                defaults={
                    'slug': slugify(transliterate(category_name)),
                    'description': f"Новости в категории {category_name}"
                }
            )
            
            if created:
                title = f"Добавлена новая работа: {instance.title}"
            else:
                title = f"Обновлена информация: {instance.title}"

            # Проверяем, не создавали ли мы уже ТАКУЮ ЖЕ новость сегодня (чтобы не спамить при частых сохранениях)
            today = timezone.now().date()
            if not News.objects.filter(title=title, created_at__date=today).exists():
                News.objects.create(
                    title=title,
                    slug=get_unique_slug(News, title),
                    category=news_category,
                    image=instance.image if hasattr(instance, 'image') and instance.image else None,
                    content=f"<p>{'Добавлена новая работа' if created else 'Обновлена информация о работе'} <strong>{instance.title}</strong> в разделе '{category_name}'.</p>"
                            f"<div>{instance.content if hasattr(instance, 'content') else ''}</div>",
                    is_active=True
                )

    elif sender == Review:
        # Для отзывов создаем новость только при одобрении
        if instance.status == 'approved':
            news_category, _ = NewsCategory.objects.get_or_create(
                name="Отзывы",
                defaults={'slug': 'reviews', 'description': 'Новости об отзывах наших клиентов'}
            )
            
            title = f"Новый отзыв от {instance.full_name}"
            # Проверяем не существует ли уже такая новость (защита от дублей)
            if not News.objects.filter(title=title).exists():
                News.objects.create(
                    title=title,
                    slug=get_unique_slug(News, title),
                    category=news_category,
                    content=f"<p>Получен новый отзыв от клиента <strong>{instance.full_name}</strong>:</p>"
                            f"<blockquote>{instance.content}</blockquote>",
                    is_active=True
                )

    elif sender == Page:
        if instance.is_active:
            news_category, _ = NewsCategory.objects.get_or_create(
                name="Страницы",
                defaults={'slug': 'pages', 'description': 'Обновления страниц сайта'}
            )
            
            if created:
                title = f"Создана новая страница: {instance.title}"
            else:
                title = f"Обновлена страница: {instance.title}"

            today = timezone.now().date()
            if not News.objects.filter(title=title, created_at__date=today).exists():
                News.objects.create(
                    title=title,
                    slug=get_unique_slug(News, title),
                    category=news_category,
                    image=instance.logo if hasattr(instance, 'logo') and instance.logo else None,
                    content=f"<p>{'Добавлена новая страница' if created else 'Обновлена информация на странице'} <strong>{instance.title}</strong>.</p>",
                    is_active=True
                )
