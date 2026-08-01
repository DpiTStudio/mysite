from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def param_replace(context, **kwargs):
    """
    Позволяет изменять или добавлять параметры GET в текущем URL,
    сохраняя остальные существующие параметры.
    Использование: {% param_replace page=2 %} или {% param_replace category=1 page=1 %}
    Для удаления параметра передайте None или пустую строку, e.g. {% param_replace category=None %}
    """
    request = context.get('request')
    if not request:
        return ''
    dict_ = request.GET.copy()
    for k, v in kwargs.items():
        if v is None or v == '':
            dict_.pop(k, None)
        else:
            dict_[k] = str(v)
    return dict_.urlencode()


@register.filter
def complexity_badge_class(complexity):
    """Возвращает CSS класс плашки для уровня сложности."""
    mapping = {
        'simple': 'bg-info bg-opacity-15 text-info border-info',
        'medium': 'bg-primary bg-opacity-15 text-primary border-primary',
        'complex': 'bg-warning bg-opacity-15 text-warning border-warning',
        'expert': 'bg-danger bg-opacity-15 text-danger border-danger',
    }
    return mapping.get(complexity, 'bg-secondary bg-opacity-15 text-secondary border-secondary')
