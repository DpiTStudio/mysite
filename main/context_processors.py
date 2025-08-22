from .models import Page, SiteSettings


def main_context(request):
    settings = SiteSettings.objects.filter(is_active=True).first()
    menu_pages = Page.objects.filter(show_in_menu=True, is_active=True).order_by(
        "order"
    )

    return {
        "site_settings": settings,
        "menu_pages": menu_pages,
    }
