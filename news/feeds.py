from datetime import datetime, time
from django.contrib.syndication.views import Feed
from django.urls import reverse
from django.utils import timezone
from .models import News


class LatestNewsFeed(Feed):
    """RSS лента для последних новостей"""
    title = "Последние новости"
    link = "/news/"
    description = "Последние новости сайта"

    def items(self):
        return News.objects.filter(is_active=True).select_related("category").order_by("-news_date", "-created_at")[:20]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.meta_description or item.content[:200]

    def item_pubdate(self, item):
        """Используем news_date как дату публикации для RSS"""
        if item.news_date:
            return timezone.make_aware(datetime.combine(item.news_date, time.min))
        return item.created_at

    def item_link(self, item):
        return reverse("news:detail", args=[item.slug])

    def item_categories(self, item):
        """Добавляем категорию в RSS"""
        if item.category:
            return [item.category.name]
        return []

