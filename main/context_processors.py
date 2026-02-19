from .models import Page, SiteSettings, AnalyticsScript
from news.models import NewsCategory
from portfolio.models import PortfolioCategory
from services.models import Service


def main_context(request):
    """
    Глобальный контекст-процессор для передачи общих данных во все шаблоны.
    """
    settings = SiteSettings.objects.filter(is_active=True).first()
    menu_pages = Page.objects.filter(show_in_menu=True, is_active=True).order_by("order")
    analytics_scripts = AnalyticsScript.objects.filter(is_active=True).order_by("position")

    # Значения по умолчанию для шапки (Главная страница)
    header_data = {
        "title": settings.site_title if settings else "DPIT-CMS",
        "description": settings.site_description if settings else "",
        "image": settings.fon_haeders.url if settings and settings.fon_haeders else None,
    }

    path = request.path.strip("/")
    path_parts = [p for p in path.split("/") if p]
    found_header = False

    if path_parts:
        app_name = path_parts[0]
        
        # 1. Логика для Новостей
        if app_name == "news":
            from news.models import News
            if "category" in path_parts and len(path_parts) > path_parts.index("category") + 1:
                slug = path_parts[path_parts.index("category") + 1]
                obj = NewsCategory.objects.filter(slug=slug, is_active=True).first()
            elif len(path_parts) > 1:
                news = News.objects.filter(slug=path_parts[1], is_active=True).first()
                obj = news.category if news else None
            else:
                obj = None
            
            if obj:
                header_data["title"] = obj.header_title or obj.name
                header_data["description"] = obj.header_description or obj.description
                if obj.header_image:
                    header_data["image"] = obj.header_image.url
                found_header = True
            else:
                header_data["title"] = "Новости и Статьи"
                header_data["description"] = "Актуальные события и обновления"
                found_header = True

        # 2. Логика для Портфолио
        elif app_name == "portfolio":
            from portfolio.models import Portfolio
            if "category" in path_parts and len(path_parts) > path_parts.index("category") + 1:
                slug = path_parts[path_parts.index("category") + 1]
                obj = PortfolioCategory.objects.filter(slug=slug, is_active=True).first()
            elif len(path_parts) > 1:
                portfolio = Portfolio.objects.filter(slug=path_parts[1], is_active=True).first()
                obj = portfolio.category if portfolio else None
            else:
                obj = None
            
            if obj:
                header_data["title"] = obj.header_title or obj.name
                header_data["description"] = obj.header_description or obj.description
                if obj.header_image:
                    header_data["image"] = obj.header_image.url
                found_header = True
            else:
                header_data["title"] = "Наше Портфолио"
                header_data["description"] = "Лучшие работы нашей команды"
                found_header = True

        # 3. Логика для Услуг
        elif app_name == "services":
            header_data["title"] = "Профессиональные услуги"
            header_data["description"] = "Решения для развития вашего бизнеса"
            found_header = True
        
        # 4. Логика для других приложений
        elif app_name == "reviews":
            header_data["title"] = "Отзывы наших клиентов"
            header_data["description"] = "Мы ценим ваше мнение о нашей работе"
            found_header = True
            
        elif app_name == "tickets":
            header_data["title"] = "Техническая поддержка"
            header_data["description"] = "Мы всегда готовы помочь вам"
            found_header = True

        elif app_name == "search":
            header_data["title"] = "Поиск по сайту"
            header_data["description"] = "Результаты поиска по вашему запросу"
            found_header = True

        # 5. Логика для обычных страниц
        if not found_header:
            slug = path_parts[-1]
            current_page = Page.objects.filter(slug=slug, is_active=True).first()
            if current_page:
                header_data["title"] = current_page.meta_title or current_page.title
                header_data["description"] = current_page.meta_description
                if current_page.fon_headers:
                    header_data["image"] = current_page.fon_headers.url

    return {
        "site_settings": settings,
        "menu_pages": menu_pages,
        "header_data": header_data,
        "analytics_scripts": analytics_scripts,
        "nav_categories": {
            "news": NewsCategory.objects.filter(is_active=True),
            "portfolio": PortfolioCategory.objects.filter(is_active=True),
            "services": Service.objects.filter(is_active=True).values_list('category', flat=True).distinct(),
        }
    }
