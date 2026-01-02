from django.db import models
from tinymce.models import HTMLField
from main.utils import RenameUploadTo
from main.models import ActiveModel, SEOModel, HeaderModel, TimestampModel


class NewsCategory(ActiveModel, SEOModel, HeaderModel):
    name = models.CharField(max_length=100, verbose_name="Название")
    slug = models.SlugField(unique=True, verbose_name="URL")
    logo = models.ImageField(upload_to=RenameUploadTo("news/categories/"), verbose_name="Логотип")
    description = models.TextField(verbose_name="Описание")
    content = HTMLField(verbose_name="Описание на странице", default="<p>Описание</p>")
    order = models.IntegerField(default=0, verbose_name="Порядок")

    class Meta:
        verbose_name = "Категория новостей"
        verbose_name_plural = "Категории новостей"
        ordering = ["order", "name"]

    def __str__(self):
        return self.name


class News(ActiveModel, SEOModel, TimestampModel):
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    slug = models.SlugField(unique=True, verbose_name="URL")
    category = models.ForeignKey(
        NewsCategory, on_delete=models.CASCADE, verbose_name="Категория"
    )
    image = models.ImageField(upload_to=RenameUploadTo("news/images/"), verbose_name="Изображение")
    content = HTMLField(verbose_name="Контент", default="<p>Контент сайта</p>")
    views = models.IntegerField(default=0, verbose_name="Просмотры")

    class Meta:
        verbose_name = "Новость"
        verbose_name_plural = "Новости"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def increment_views(self):
        self.views += 1
        # Используем update для избежания лишних вызовов save() и сигналов
        News.objects.filter(pk=self.pk).update(views=self.views)


class Comment(TimestampModel):
    news = models.ForeignKey(
        News,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    rating = models.IntegerField(default=0)
    text = models.TextField()

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Комментарий к {self.news.title}"
