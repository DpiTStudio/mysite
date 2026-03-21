from django import template

register = template.Library()


@register.inclusion_tag("includes/breadcrumbs.html", takes_context=True)
def breadcrumbs(context):
    """
    Создает хлебные крошки для навигации
    """
    request = context["request"]
    path = request.path
    breadcrumbs_list = []
    
    # Всегда добавляем главную
    breadcrumbs_list.append({
        "title": "Главная",
        "url": "/",
        "active": path == "/",
    })
    
    # Разбираем путь
    path_parts = [p for p in path.split("/") if p]
    
    current_path = ""
    skip_next = False
    
    for i, part in enumerate(path_parts):
        if skip_next:
            skip_next = False
            continue
            
        current_path += f"/{part}"
        is_last = i == len(path_parts) - 1
        
        # Определяем название для части пути
        title = part.replace("-", " ").replace("_", " ").title()
        
        # Специальные случаи
        translations = {
            "news": "Новости",
            "portfolio": "Портфолио",
            "reviews": "Отзывы",
            "search": "Поиск",
            "feed": "RSS лента",
            "services": "Услуги",
            "cart": "Корзина",
            "favorites": "Избранное",
            "knowledge-base": "База знаний",
            "accounts": "Аккаунт",
            "login": "Вход",
            "logout": "Выход",
            "signup": "Регистрация",
            "profile": "Профиль",
            "tickets": "Поддержка",
            "checkout": "Оформление заказа",
            "password-reset": "Сброс пароля",
            "password-change": "Изменение пароля",
            "password_reset": "Сброс пароля",
            "password_change": "Изменение пароля",
            "admin": "Панель администратора",
            "mail": "Почта",
        }
        
        if part == "category":
            # Пропускаем "category", следующая часть будет названием категории
            skip_next = True
            continue
        elif part in translations:
            title = translations[part]
        
        breadcrumbs_list.append({
            "title": title,
            "url": current_path,
            "active": is_last,
        })
    
    return {"breadcrumbs": breadcrumbs_list}

