from django.db import models
from django.utils import timezone
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
    """
    Модель для дневной сводки новостей.
    Одна запись News содержит все события за один день (год, месяц, день).
    """
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    slug = models.SlugField(unique=True, verbose_name="URL")
    category = models.ForeignKey(
        NewsCategory, on_delete=models.CASCADE, verbose_name="Категория"
    )
    news_date = models.DateField(
        default=timezone.now, 
        verbose_name="Дата новости",
        help_text="Дата, к которой относятся события (год, месяц, день)"
    )
    image = models.ImageField(
        upload_to=RenameUploadTo("news/images/"), 
        verbose_name="Изображение",
        blank=True,
        null=True
    )
    content = HTMLField(verbose_name="Контент", default="<p>Контент сайта</p>")
    views = models.IntegerField(default=0, verbose_name="Просмотры")

    class Meta:
        verbose_name = "Новость"
        verbose_name_plural = "Новости"
        ordering = ["-news_date", "-created_at"]
        # Уникальность: одна новость на дату в рамках категории
        unique_together = [['category', 'news_date']]

    def __str__(self):
        return f"{self.title} ({self.news_date.strftime('%d.%m.%Y')})"

    def increment_views(self):
        self.views += 1
        # Используем update для избежания лишних вызовов save() и сигналов
        News.objects.filter(pk=self.pk).update(views=self.views)
    
    def get_events_count(self):
        """Возвращает количество событий за день"""
        return self.events.count()


class DailyEvent(TimestampModel):
    """
    Модель для отдельного события в рамках дневной новости.
    Несколько событий могут быть привязаны к одной новости (одному дню).
    """
    news = models.ForeignKey(
        News,
        on_delete=models.CASCADE,
        related_name="events",
        verbose_name="Новость дня"
    )
    event_type = models.CharField(
        max_length=50,
        verbose_name="Тип события",
        choices=[
            ('portfolio_added', 'Добавлена работа в портфолио'),
            ('portfolio_updated', 'Обновлена работа в портфолио'),
            ('review_approved', 'Одобрен отзыв'),
            ('page_created', 'Создана страница'),
            ('page_updated', 'Обновлена страница'),
            ('service_added', 'Добавлена услуга'),
            ('service_updated', 'Обновлена услуга'),
            ('other', 'Другое событие'),
        ]
    )
    title = models.CharField(max_length=300, verbose_name="Заголовок события")
    description = HTMLField(verbose_name="Описание события")
    related_object_id = models.IntegerField(
        null=True, 
        blank=True,
        verbose_name="ID связанного объекта"
    )
    related_object_type = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="Тип связанного объекта"
    )
    image = models.ImageField(
        upload_to=RenameUploadTo("news/events/"),
        verbose_name="Изображение события",
        blank=True,
        null=True
    )
    order = models.IntegerField(default=0, verbose_name="Порядок отображения")

    class Meta:
        verbose_name = "Событие дня"
        verbose_name_plural = "События дня"
        ordering = ['order', '-created_at']

    def __str__(self):
        return f"{self.title} ({self.created_at.strftime('%H:%M')})"


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
