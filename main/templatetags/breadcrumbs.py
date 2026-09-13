from django import template

register = template.Library()

DICTIONARY = {
    "news": "Новости",
    "portfolio": "Портфолио",
    "reviews": "Отзывы",
    "services": "Услуги",
    "cart": "Корзина",
    "favorites": "Избранное",
    "knowledge-base": "База знаний",
    "knowledge_base": "База знаний",
    "accounts": "Личный кабинет",
    "login": "Вход в систему",
    "logout": "Выход",
    "signup": "Регистрация",
    "register": "Регистрация",
    "profile": "Профиль",
    "tickets": "Служба поддержки",
    "create": "Создание",
    "checkout": "Оформление заказа",
    "search": "Поиск по сайту",
    "feed": "RSS лента",
    "password-reset": "Сброс пароля",
    "password-change": "Изменение пароля",
    "password_reset": "Сброс пароля",
    "password_change": "Изменение пароля",
    "admin": "Панель администратора",
    "mail": "Почта",
    "send-test": "Тестовое письмо",
    "order": "Заказ",
    "category": "Категория",
    "article": "Статья",
    "page": "Страница",
    "date": "Архив",
    "success": "Успешное завершение",
}


@register.inclusion_tag("includes/breadcrumbs.html", takes_context=True)
def breadcrumbs(context):
    """
    Создает читаемые хлебные крошки для навигации на русском языке.
    """
    request = context.get("request")
    if not request:
        return {"breadcrumbs": []}

    path = request.path
    if path == "/":
        return {"breadcrumbs": [{"title": "Главная", "url": "/", "active": True}]}

    path_parts = [p for p in path.strip("/").split("/") if p]
    breadcrumbs_list = [
        {"title": "Главная", "url": "/", "active": False}
    ]

    app_name = path_parts[0] if path_parts else ""

    try:
        # 1. НОВОСТИ
        if app_name == "news":
            breadcrumbs_list.append({"title": "Новости", "url": "/news/", "active": len(path_parts) == 1})

            if len(path_parts) > 1:
                if path_parts[1] == "category" and len(path_parts) > 2:
                    cat_slug = path_parts[2]
                    category = context.get("category")
                    if not category:
                        from news.models import NewsCategory
                        category = NewsCategory.objects.filter(slug=cat_slug, is_active=True).first()
                    title = category.name if category else cat_slug.replace("-", " ").capitalize()
                    breadcrumbs_list.append({"title": title, "url": f"/news/category/{cat_slug}/", "active": True})

                elif path_parts[1] == "search":
                    breadcrumbs_list.append({"title": "Поиск новостей", "url": "/news/search/", "active": True})

                elif path_parts[1] == "date":
                    breadcrumbs_list.append({"title": "Архив новостей", "url": path, "active": True})

                elif path_parts[1] == "feed":
                    breadcrumbs_list.append({"title": "RSS лента", "url": "/news/feed/", "active": True})

                else:
                    news_slug = path_parts[1]
                    news = context.get("news") or context.get("article") or context.get("news_item")
                    if not news:
                        from news.models import News
                        news = News.objects.filter(slug=news_slug, is_active=True).first()

                    if news:
                        if news.category:
                            breadcrumbs_list.append({
                                "title": news.category.name,
                                "url": f"/news/category/{news.category.slug}/",
                                "active": False
                            })
                        breadcrumbs_list.append({"title": news.title, "url": path, "active": True})
                    else:
                        title = news_slug.replace("-", " ").capitalize()
                        breadcrumbs_list.append({"title": title, "url": path, "active": True})

        # 2. ПОРТФОЛИО
        elif app_name == "portfolio":
            breadcrumbs_list.append({"title": "Портфолио", "url": "/portfolio/", "active": len(path_parts) == 1})

            if len(path_parts) > 1:
                if path_parts[1] == "category" and len(path_parts) > 2:
                    cat_slug = path_parts[2]
                    category = context.get("category")
                    if not category:
                        from portfolio.models import PortfolioCategory
                        category = PortfolioCategory.objects.filter(slug=cat_slug, is_active=True).first()
                    title = category.name if category else cat_slug.replace("-", " ").capitalize()
                    breadcrumbs_list.append({"title": title, "url": f"/portfolio/category/{cat_slug}/", "active": True})
                else:
                    p_slug = path_parts[1]
                    portfolio = context.get("portfolio") or context.get("item")
                    if not portfolio:
                        from portfolio.models import Portfolio
                        portfolio = Portfolio.objects.filter(slug=p_slug, is_active=True).first()

                    if portfolio:
                        if portfolio.category:
                            breadcrumbs_list.append({
                                "title": portfolio.category.name,
                                "url": f"/portfolio/category/{portfolio.category.slug}/",
                                "active": False
                            })
                        breadcrumbs_list.append({"title": portfolio.title, "url": path, "active": True})
                    else:
                        title = p_slug.replace("-", " ").capitalize()
                        breadcrumbs_list.append({"title": title, "url": path, "active": True})

        # 3. УСЛУГИ
        elif app_name == "services":
            breadcrumbs_list.append({"title": "Услуги", "url": "/services/", "active": len(path_parts) == 1})

            if len(path_parts) > 1:
                if path_parts[1] == "category" and len(path_parts) > 2:
                    cat_slug = path_parts[2]
                    category = context.get("category")
                    if not category:
                        from services.models import ServiceCategory
                        category = ServiceCategory.objects.filter(slug=cat_slug, is_active=True).first()
                    title = category.name if category else cat_slug.replace("-", " ").capitalize()
                    breadcrumbs_list.append({"title": title, "url": f"/services/category/{cat_slug}/", "active": True})

                elif path_parts[1] == "search":
                    breadcrumbs_list.append({"title": "Поиск услуг", "url": "/services/search/", "active": True})

                elif path_parts[1] == "order" and len(path_parts) > 2:
                    s_slug = path_parts[2]
                    service = context.get("service")
                    if not service:
                        from services.models import Service
                        service = Service.objects.filter(slug=s_slug, is_active=True).first()
                    if service:
                        breadcrumbs_list.append({
                            "title": service.title,
                            "url": f"/services/{service.slug}/",
                            "active": False
                        })
                    breadcrumbs_list.append({"title": "Оформление заказа", "url": path, "active": True})

                else:
                    s_slug = path_parts[1]
                    service = context.get("service")
                    if not service:
                        from services.models import Service
                        service = Service.objects.filter(slug=s_slug, is_active=True).first()

                    if service:
                        if service.category:
                            breadcrumbs_list.append({
                                "title": service.category.name,
                                "url": f"/services/category/{service.category.slug}/",
                                "active": False
                            })
                        breadcrumbs_list.append({"title": service.title, "url": path, "active": True})
                    else:
                        title = s_slug.replace("-", " ").capitalize()
                        breadcrumbs_list.append({"title": title, "url": path, "active": True})

        # 4. БАЗА ЗНАНИЙ
        elif app_name == "knowledge-base" or app_name == "knowledge_base":
            breadcrumbs_list.append({"title": "База знаний", "url": "/knowledge-base/", "active": len(path_parts) == 1})

            if len(path_parts) > 1:
                if path_parts[1] == "category" and len(path_parts) > 2:
                    cat_slug = path_parts[2]
                    category = context.get("category")
                    if not category:
                        from knowledge_base.models import Category as KBCategory
                        category = KBCategory.objects.filter(slug=cat_slug).first()
                    title = category.name if category else cat_slug.replace("-", " ").capitalize()
                    breadcrumbs_list.append({"title": title, "url": f"/knowledge-base/category/{cat_slug}/", "active": True})

                elif path_parts[1] == "article" and len(path_parts) > 2:
                    art_slug = path_parts[2]
                    article = context.get("article") or context.get("kb_article")
                    if not article:
                        from knowledge_base.models import Article as KBArticle
                        article = KBArticle.objects.filter(slug=art_slug).first()

                    if article:
                        if article.category:
                            breadcrumbs_list.append({
                                "title": article.category.name,
                                "url": f"/knowledge-base/category/{article.category.slug}/",
                                "active": False
                            })
                        breadcrumbs_list.append({"title": article.title, "url": path, "active": True})
                    else:
                        title = art_slug.replace("-", " ").capitalize()
                        breadcrumbs_list.append({"title": title, "url": path, "active": True})

        # 5. ТИКЕТЫ / ТЕХПОДДЕРЖКА
        elif app_name == "tickets":
            breadcrumbs_list.append({"title": "Служба поддержки", "url": "/tickets/", "active": len(path_parts) == 1})

            if len(path_parts) > 1:
                if path_parts[1] == "create":
                    breadcrumbs_list.append({"title": "Создание обращения", "url": "/tickets/create/", "active": True})
                else:
                    ticket_id = path_parts[1]
                    ticket = context.get("ticket")
                    if not ticket and ticket_id.isdigit():
                        from tickets.models import Ticket
                        ticket = Ticket.objects.filter(pk=int(ticket_id)).first()

                    if ticket:
                        title = f"Обращение №{ticket.id}: {ticket.subject}"
                    else:
                        title = f"Обращение №{ticket_id}"

                    if len(path_parts) > 2 and path_parts[2] == "close":
                        breadcrumbs_list.append({"title": title, "url": f"/tickets/{ticket_id}/", "active": False})
                        breadcrumbs_list.append({"title": "Закрытие обращения", "url": path, "active": True})
                    else:
                        breadcrumbs_list.append({"title": title, "url": path, "active": True})

        # 6. АККАУНТЫ
        elif app_name == "accounts":
            breadcrumbs_list.append({"title": "Личный кабинет", "url": "/accounts/profile/", "active": len(path_parts) == 1})

            if len(path_parts) > 1:
                action = path_parts[1]
                translations = {
                    "login": "Вход в систему",
                    "logout": "Выход",
                    "register": "Регистрация",
                    "signup": "Регистрация",
                    "profile": "Профиль",
                    "password-reset": "Сброс пароля",
                    "password-change": "Изменение пароля",
                    "password_reset": "Сброс пароля",
                    "password_change": "Изменение пароля",
                }
                title = translations.get(action, action.replace("-", " ").capitalize())
                breadcrumbs_list.append({"title": title, "url": path, "active": True})

        # 7. КОРЗИНА
        elif app_name == "cart":
            breadcrumbs_list.append({"title": "Корзина", "url": "/cart/", "active": len(path_parts) == 1})

            if len(path_parts) > 1:
                if path_parts[1] == "checkout":
                    breadcrumbs_list.append({"title": "Оформление заказа", "url": "/cart/checkout/", "active": True})
                elif path_parts[1] == "success" and len(path_parts) > 2:
                    order_id = path_parts[2]
                    breadcrumbs_list.append({"title": f"Заказ №{order_id}", "url": path, "active": True})

        # 8. ОТЗЫВЫ
        elif app_name == "reviews":
            breadcrumbs_list.append({"title": "Отзывы", "url": "/reviews/", "active": len(path_parts) == 1})

            if len(path_parts) > 1 and path_parts[1] == "create":
                breadcrumbs_list.append({"title": "Оставить отзыв", "url": "/reviews/create/", "active": True})

        # 9. ИЗБРАННОЕ
        elif app_name == "favorites":
            breadcrumbs_list.append({"title": "Избранное", "url": "/favorites/", "active": True})

        # 10. ПОЧТА
        elif app_name == "mail":
            breadcrumbs_list.append({"title": "Почта", "url": "/mail/", "active": len(path_parts) == 1})

            if len(path_parts) > 1 and path_parts[1] == "send-test":
                breadcrumbs_list.append({"title": "Тестовое письмо", "url": "/mail/send-test/", "active": True})

        # 11. ПОИСК
        elif app_name == "search":
            breadcrumbs_list.append({"title": "Поиск по сайту", "url": "/search/", "active": True})

        # 12. СТАТИЧЕСКИЕ СТРАНИЦЫ /page/<slug>/
        elif app_name == "page" and len(path_parts) > 1:
            page_slug = path_parts[1]
            page = context.get("page")
            if not page:
                from main.models import Page
                page = Page.objects.filter(slug=page_slug, is_active=True).first()

            title = page.title if page else page_slug.replace("-", " ").capitalize()
            breadcrumbs_list.append({"title": title, "url": path, "active": True})

        # 13. РЕЗЕРВНАЯ ОБРАБОТКА ДЛЯ ИНЫХ СТРАНИЦ
        else:
            current_path = ""
            for i, part in enumerate(path_parts):
                current_path += f"/{part}"
                is_last = (i == len(path_parts) - 1)

                if is_last and context.get("header_data", {}).get("title"):
                    title = context["header_data"]["title"]
                elif part in DICTIONARY:
                    title = DICTIONARY[part]
                else:
                    title = part.replace("-", " ").replace("_", " ").title()

                breadcrumbs_list.append({
                    "title": title,
                    "url": current_path,
                    "active": is_last
                })
    except Exception:
        pass

    return {"breadcrumbs": breadcrumbs_list}


