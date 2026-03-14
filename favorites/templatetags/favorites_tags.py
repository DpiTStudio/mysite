from django import template
from django.contrib.contenttypes.models import ContentType

register = template.Library()


@register.filter
def is_favorite(obj, user):
    """
    Фильтр: проверяет, добавлен ли объект в избранное пользователя.
    
    Использование: {{ obj|is_favorite:user }}
    Возвращает: bool
    """
    if not user or not user.is_authenticated:
        return False
    from favorites.models import Favorite
    ct = ContentType.objects.get_for_model(obj)
    return Favorite.objects.filter(user=user, content_type=ct, object_id=obj.pk).exists()


@register.filter
def fav_count(obj):
    """
    Фильтр: возвращает количество добавлений объекта в избранное.
    
    Использование: {{ obj|fav_count }}
    Возвращает: int
    """
    from favorites.models import Favorite
    ct = ContentType.objects.get_for_model(obj)
    return Favorite.objects.filter(content_type=ct, object_id=obj.pk).count()
