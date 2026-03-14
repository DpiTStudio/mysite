from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.views.decorators.http import require_POST
from .models import Favorite


@login_required
@require_POST
def toggle_favorite(request, app_label, model_name, object_id):
    """
    Добавляет или удаляет объект из избранного текущего пользователя.

    URL: /favorites/toggle/<app_label>/<model_name>/<object_id>/
    Метод: POST (CSRF-защита)
    Ответ: JSON { "is_favorite": bool, "count": int }

    Пример использования в шаблоне:
        hx-post="{% url 'favorites:toggle' 'news' 'news' news.id %}"
    """
    try:
        ct = ContentType.objects.get(app_label=app_label, model=model_name)
    except ContentType.DoesNotExist:
        return JsonResponse({'error': 'Тип объекта не найден'}, status=404)

    fav, created = Favorite.objects.get_or_create(
        user=request.user,
        content_type=ct,
        object_id=object_id,
    )

    if not created:
        # Уже было в избранном — удаляем
        fav.delete()
        is_favorite = False
    else:
        is_favorite = True

    # Количество лайков этого объекта
    count = Favorite.objects.filter(content_type=ct, object_id=object_id).count()

    return JsonResponse({
        'is_favorite': is_favorite,
        'count': count,
    })


@login_required
def favorites_list(request):
    """Страница со всеми избранными объектами пользователя."""
    from django.shortcuts import render
    favorites = Favorite.objects.filter(user=request.user).select_related('content_type')

    # Группируем по типу объекта
    grouped = {}
    for fav in favorites:
        obj = fav.content_object
        if obj is None:
            continue  # Объект был удалён
        key = fav.content_type.model
        if key not in grouped:
            grouped[key] = {'label': fav.content_type.name, 'items': []}
        grouped[key]['items'].append(obj)

    return render(request, 'favorites/list.html', {
        'grouped': grouped,
        'favorites_count': favorites.count(),
    })
