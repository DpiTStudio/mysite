from .models import Page, SiteSettings


def main_context(request):
    settings = SiteSettings.objects.filter(is_active=True).first()
    menu_pages = Page.objects.filter(show_in_menu=True, is_active=True).order_by(
        "order"
    )

    # Определяем текущую страницу по URL
    current_page = None
    if request.path != "/":  # Если не главная страница
        try:
            # Пытаемся найти страницу по части URL
            path_parts = request.path.strip("/").split("/")
            if path_parts:
                slug = path_parts[-1]
                current_page = Page.objects.filter(slug=slug, is_active=True).first()
        except:
            pass

    return {
        "site_settings": settings,
        "menu_pages": menu_pages,
        "current_page": current_page,  # Добавляем текущую страницу в контекст
        # "social_links": SocialLink.objects.filter(is_active=True),
    }
