from .models import Page, SiteSettings


def main_context(request):
    settings = SiteSettings.objects.filter(is_active=True).first()
    menu_pages = Page.objects.filter(show_in_menu=True, is_active=True).order_by(
        "order"
    )

    # Определяем текущую страницу или категорию для шапки
    header_data = {
        "title": settings.site_title if settings else "DPIT-CMS",
        "description": settings.site_description if settings else "",
        "image": settings.fon_haeders.url if settings and settings.fon_haeders else None,
    }

    current_page = None
    path = request.path.strip("/")
    path_parts = [p for p in path.split("/") if p]

    found_header = False

    if path_parts:
        # Пытаемся определить, находимся ли мы в новостях или портфолио
        if path_parts[0] == "news":
            from news.models import NewsCategory, News
            if len(path_parts) > 2 and path_parts[1] == "category":
                category = NewsCategory.objects.filter(slug=path_parts[2], is_active=True).first()
                if category:
                    header_data["title"] = category.header_title or category.name
                    header_data["description"] = category.header_description or category.description
                    if category.header_image:
                        header_data["image"] = category.header_image.url
                    found_header = True
            elif len(path_parts) > 1: # Это может быть новость
                news = News.objects.filter(slug=path_parts[1], is_active=True).first()
                if news and news.category:
                    header_data["title"] = news.category.header_title or news.category.name
                    header_data["description"] = news.category.header_description or news.category.description
                    if news.category.header_image:
                        header_data["image"] = news.category.header_image.url
                    found_header = True

        elif path_parts[0] == "portfolio":
            from portfolio.models import PortfolioCategory, Portfolio
            if len(path_parts) > 2 and path_parts[1] == "category":
                category = PortfolioCategory.objects.filter(slug=path_parts[2], is_active=True).first()
                if category:
                    header_data["title"] = category.header_title or category.name
                    header_data["description"] = category.header_description or category.description
                    if category.header_image:
                        header_data["image"] = category.header_image.url
                    found_header = True
            elif len(path_parts) > 1: # Это может быть портфолио
                portfolio = Portfolio.objects.filter(slug=path_parts[1], is_active=True).first()
                if portfolio and portfolio.category:
                    header_data["title"] = portfolio.category.header_title or portfolio.category.name
                    header_data["description"] = portfolio.category.header_description or portfolio.category.description
                    if portfolio.category.header_image:
                        header_data["image"] = portfolio.category.header_image.url
                    found_header = True
        
        # Если хидер еще не найден, проверяем обычные страницы
        if not found_header:
            slug = path_parts[-1]
            current_page = Page.objects.filter(slug=slug, is_active=True).first()
            if current_page:
                header_data["title"] = current_page.title
                header_data["description"] = current_page.meta_description
                if current_page.fon_headers:
                    header_data["image"] = current_page.fon_headers.url

    return {
        "site_settings": settings,
        "menu_pages": menu_pages,
        "current_page": current_page,
        "header_data": header_data,
    }
