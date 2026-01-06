from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import slugify
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


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
    """Генерирует уникальный slug для модели"""
    base_slug = slugify(transliterate(title))
    if not base_slug:
        base_slug = "news-item"
    slug = base_slug
    num = 1
    while model_class.objects.filter(slug=slug).exists():
        slug = f"{base_slug}-{num}"
        num += 1
    return slug


def get_or_create_daily_news(category, event_date):
    """
    Получает или создает новость для указанной даты и категории.
    
    Args:
        category: Категория новостей (NewsCategory)
        event_date: Дата события (date object)
    
    Returns:
        News: Объект новости для указанной даты
    """
    from news.models import News
    
    # Пытаемся найти существующую новость для этой даты и категории
    daily_news = News.objects.filter(
        category=category,
        news_date=event_date
    ).first()
    
    if daily_news:
        logger.info(f"Найдена существующая новость для {event_date}: {daily_news.title}")
        return daily_news
    
    # Создаем новую дневную новость
    title = f"События {event_date.strftime('%d.%m.%Y')} - {category.name}"
    slug = get_unique_slug(News, f"{category.slug}-{event_date.strftime('%Y-%m-%d')}")
    
    daily_news = News.objects.create(
        title=title,
        slug=slug,
        category=category,
        news_date=event_date,
        content=f"<h2>События дня {event_date.strftime('%d.%m.%Y')}</h2><p>В этот день произошли следующие события:</p>",
        is_active=True
    )
    
    logger.info(f"Создана новая дневная новость: {daily_news.title}")
    return daily_news


def add_event_to_daily_news(news, event_type, title, description, related_obj=None, image=None):
    """
    Добавляет событие к дневной новости.
    
    Args:
        news: Объект News (дневная новость)
        event_type: Тип события (строка из choices)
        title: Заголовок события
        description: Описание события (HTML)
        related_obj: Связанный объект (опционально)
        image: Изображение события (опционально)
    
    Returns:
        DailyEvent: Созданное событие
    """
    from news.models import DailyEvent
    
    # Проверяем, не добавляли ли мы уже это событие (защита от дублей)
    existing_event = DailyEvent.objects.filter(
        news=news,
        title=title
    ).first()
    
    if existing_event:
        logger.info(f"Событие '{title}' уже существует для новости {news.title}")
        return existing_event
    
    # Определяем порядок (последнее событие будет первым в списке)
    max_order = DailyEvent.objects.filter(news=news).count()
    
    event_data = {
        'news': news,
        'event_type': event_type,
        'title': title,
        'description': description,
        'order': max_order,
    }
    
    if related_obj:
        event_data['related_object_id'] = related_obj.id
        event_data['related_object_type'] = related_obj.__class__.__name__
    
    if image:
        event_data['image'] = image
    
    event = DailyEvent.objects.create(**event_data)
    logger.info(f"Добавлено событие '{title}' к новости {news.title}")
    
    # Обновляем контент новости (добавляем краткую информацию о событии)
    update_news_content(news)
    
    return event


def update_news_content(news):
    """
    Обновляет контент новости на основе всех её событий.
    
    Args:
        news: Объект News
    """
    events = news.events.all().order_by('order', '-created_at')
    events_count = events.count()
    
    # Формируем новый контент
    content_parts = [
        f"<h2>События дня {news.news_date.strftime('%d.%m.%Y')}</h2>",
        f"<p>В этот день произошло событий: <strong>{events_count}</strong></p>",
        "<hr>"
    ]
    
    for idx, event in enumerate(events, 1):
        content_parts.append(f"<h3>{idx}. {event.title}</h3>")
        content_parts.append(f"<p><em>Время: {event.created_at.strftime('%H:%M')}</em></p>")
        content_parts.append(event.description)
        content_parts.append("<hr>")
    
    news.content = "\n".join(content_parts)
    news.save(update_fields=['content'])
    logger.info(f"Обновлен контент новости {news.title} ({events_count} событий)")


@receiver(post_save)
def auto_create_news_event(sender, instance, created, **kwargs):
    """
    Автоматически создает события в дневных новостях при изменении объектов.
    События группируются по дате (год, месяц, день).
    """
    # Избегаем рекурсии
    from news.models import News, NewsCategory, DailyEvent
    if sender in [News, NewsCategory, DailyEvent]:
        return

    # Импортируем модели
    from portfolio.models import Portfolio
    from reviews.models import Review
    from main.models import Page
    
    # Получаем текущую дату
    today = timezone.now().date()
    
    try:
        if sender == Portfolio and instance.is_active:
            # Получаем или создаем категорию новостей
            category_name = instance.category.name
            news_category, _ = NewsCategory.objects.get_or_create(
                name=category_name,
                defaults={
                    'slug': slugify(transliterate(category_name)),
                    'description': f"Новости в категории {category_name}",
                    'logo': instance.category.logo if hasattr(instance.category, 'logo') else None,
                }
            )
            
            # Получаем или создаем дневную новость
            daily_news = get_or_create_daily_news(news_category, today)
            
            # Определяем тип события и заголовок
            if created:
                event_type = 'portfolio_added'
                event_title = f"Добавлена новая работа: {instance.title}"
                event_description = f"<p>Добавлена новая работа <strong>{instance.title}</strong> в разделе '{category_name}'.</p>"
            else:
                event_type = 'portfolio_updated'
                event_title = f"Обновлена работа: {instance.title}"
                event_description = f"<p>Обновлена информация о работе <strong>{instance.title}</strong> в разделе '{category_name}'.</p>"
            
            # Добавляем детали, если есть контент
            if hasattr(instance, 'content') and instance.content:
                event_description += f"<div>{instance.content}</div>"
            
            # Добавляем событие к дневной новости
            add_event_to_daily_news(
                news=daily_news,
                event_type=event_type,
                title=event_title,
                description=event_description,
                related_obj=instance,
                image=instance.image if hasattr(instance, 'image') and instance.image else None
            )
            
        elif sender == Review and instance.status == 'approved':
            # Получаем или создаем категорию для отзывов
            news_category, _ = NewsCategory.objects.get_or_create(
                name="Отзывы",
                defaults={
                    'slug': 'reviews',
                    'description': 'Новости об отзывах наших клиентов'
                }
            )
            
            # Получаем или создаем дневную новость
            daily_news = get_or_create_daily_news(news_category, today)
            
            # Добавляем событие
            event_title = f"Новый отзыв от {instance.full_name}"
            event_description = f"<p>Получен новый отзыв от клиента <strong>{instance.full_name}</strong>:</p><blockquote>{instance.content}</blockquote>"
            
            add_event_to_daily_news(
                news=daily_news,
                event_type='review_approved',
                title=event_title,
                description=event_description,
                related_obj=instance
            )
            
        elif sender == Page and instance.is_active:
            # Получаем или создаем категорию для страниц
            news_category, _ = NewsCategory.objects.get_or_create(
                name="Страницы",
                defaults={
                    'slug': 'pages',
                    'description': 'Обновления страниц сайта'
                }
            )
            
            # Получаем или создаем дневную новость
            daily_news = get_or_create_daily_news(news_category, today)
            
            # Определяем тип события
            if created:
                event_type = 'page_created'
                event_title = f"Создана новая страница: {instance.title}"
                event_description = f"<p>Добавлена новая страница <strong>{instance.title}</strong>.</p>"
            else:
                event_type = 'page_updated'
                event_title = f"Обновлена страница: {instance.title}"
                event_description = f"<p>Обновлена информация на странице <strong>{instance.title}</strong>.</p>"
            
            # Добавляем событие
            add_event_to_daily_news(
                news=daily_news,
                event_type=event_type,
                title=event_title,
                description=event_description,
                related_obj=instance,
                image=instance.logo if hasattr(instance, 'logo') and instance.logo else None
            )
    
    except Exception as e:
        logger.error(f"Ошибка при создании события новости: {e}", exc_info=True)
