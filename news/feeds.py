from django.contrib.syndication.views import Feed
from django.urls import reverse
from .models import News


class LatestNewsFeed(Feed):
    """RSS лента для последних новостей"""
    title = "Последние новости"
    link = "/news/"
    description = "Последние новости сайта"

    def items(self):
        return News.objects.filter(is_active=True).order_by("-created_at")[:20]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.meta_description

    def item_pubdate(self, item):
        return item.created_at

    def item_link(self, item):
        # Django автоматически сделает URL абсолютным
        return reverse("news:detail", args=[item.slug])

