from django.db import models
from tinymce.models import HTMLField
from .utils import RenameUploadTo


class ActiveModel(models.Model):
    """Абстрактная модель для управления активностью записи."""
    is_active = models.BooleanField(default=True, verbose_name="Активно")

    class Meta:
        abstract = True


class TimestampModel(models.Model):
    """Абстрактная модель для хранения меток времени."""
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        abstract = True


class SEOModel(models.Model):
    """Абстрактная модель для SEO настроек."""
    meta_title = models.CharField(
        max_length=200, 
        verbose_name="Мета заголовок", 
        blank=True,
        help_text="Заголовок страницы для поисковых систем."
    )
    meta_keywords = models.CharField(
        max_length=200, 
        verbose_name="Ключевые слова", 
        blank=True,
        help_text="Ключевые слова через запятую."
    )
    meta_description = models.CharField(
        max_length=255, 
        verbose_name="Мета описание", 
        blank=True,
        help_text="Краткое описание для поисковых систем."
    )

    class Meta:
        abstract = True


class HeaderModel(models.Model):
    """Абстрактная модель для настройки шапки страницы."""
    header_image = models.ImageField(
        upload_to=RenameUploadTo("headers/"),
        verbose_name="Изображение шапки",
        blank=True,
        null=True,
        help_text="Фоновое изображение для заголовка страницы."
    )
    header_title = models.CharField(
        max_length=200, 
        verbose_name="Заголовок шапки", 
        blank=True, 
        null=True,
        help_text="Оставьте пустым для использования стандартного названия."
    )
    header_description = models.TextField(
        verbose_name="Описание шапки", 
        blank=True, 
        null=True,
        help_text="Дополнительный текст под заголовком."
    )

    class Meta:
        abstract = True



class SiteSettings(ActiveModel, SEOModel):
    """
    Модель для хранения глобальных настроек сайта.

    Содержит основные параметры, такие как название, слоган, контактная информация,
    SEO-настройки, логотип и фавикон. Предназначена для управления общей конфигурацией
    сайта через административную панель. Позволяет иметь только одну активную запись
    (логически — настройки одного сайта), удаление которой запрещено.
    """

    site_title = models.CharField(max_length=200, verbose_name="Название сайта")
    """
    Название сайта, отображаемое в заголовках страниц и интерфейсе.
    """

    site_slogan = models.CharField(max_length=30, verbose_name="Слоган")
    """
    Краткий слоган сайта, может использоваться в шапке или рекламных блоках.
    """

    site_description = models.TextField(verbose_name="Описание сайта")
    """
    Полное текстовое описание сайта, применяемое в мета-тегах и на страницах.
    """

    site_email = models.EmailField(max_length=20, verbose_name="Электронная почта")
    """
    Основной email для связи с администраторами сайта.
    """

    site_phone_1 = models.CharField(max_length=11, verbose_name="Телефон 1")
    """
    Первый контактный телефон (например, основной номер поддержки).
    """

    site_phone_2 = models.CharField(max_length=11, verbose_name="Телефон 2")
    """
    Второй контактный телефон (дополнительный или альтернативный номер).
    """

    content = HTMLField(verbose_name="Контент", default="<p>Контент сайта</p>")
    """
    Основной HTML-контент сайта, может использоваться на главной странице
    или в других общих блоках. По умолчанию содержит заглушку.
    """

    logo = models.ImageField(upload_to=RenameUploadTo("logos/"), verbose_name="Логотип")
    """
    Логотип сайта. Загружается в папку 'logos/'. Отображается в шапке сайта.
    """

    favicon = models.ImageField(upload_to=RenameUploadTo("favicons/"), verbose_name="Фавикон")
    """
    Фавикон сайта — маленькая иконка, отображаемая в браузерной вкладке.
    Загружается в папку 'favicons/'.
    """

    fon_haeders = models.ImageField(upload_to=RenameUploadTo("fon_haeders/"), verbose_name="Фон шапки")
    """
    Фон шапки. Загружается в папку 'fon_haeders/'. Отображается в шапке сайта.
    """

    site_domain = models.CharField(
        max_length=200,
        verbose_name="Домен сайта",
        blank=True,
        null=True,
        help_text="Домен сайта для отображения в шапке (например, dpit-cms.ru). Если не указан, будет использоваться текущий хост.",
    )
    """
    Домен сайта для отображения в шапке. Если не указан, используется текущий хост.
    """

    def __str__(self):
        """
        Возвращает строковое представление объекта — название сайта.

        Используется в интерфейсе админки Django для отображения записей.

        :return: Название сайта (site_title).
        :rtype: str
        """
        return self.site_title

    def has_delete_permission(self, request, obj=None):
        """
        Запрещает удаление объекта настроек сайта.

        Перегруженный метод, который всегда возвращает False,
        чтобы предотвратить удаление записи через административный интерфейс.

        :param request: Объект HTTP-запроса.
        :type request: django.http.HttpRequest
        :param obj: Объект настроек (не используется).
        :type obj: SiteSettings or None
        :return: Всегда False — удаление запрещено.
        :rtype: bool
        """
        return False

    class Meta:
        """
        Метакласс для настройки отображения модели в Django.

        Задаёт читаемые названия для модели в интерфейсе админки.
        """

        verbose_name = "Настройки сайта"
        verbose_name_plural = "Настройки сайта"


class Page(ActiveModel, TimestampModel, SEOModel):
    """
    Модель для представления страницы сайта.

    Описывает основные атрибуты страницы, включая заголовок, URL, мета-теги,
    контент и параметры отображения в меню и порядка сортировки.
    Поддерживает SEO-оптимизацию и возможность добавления логотипа.
    """

    title = models.CharField(
        max_length=200,
        verbose_name="Заголовок страницы",
        help_text="Введите заголовок страницы, отображаемый в браузере и на сайте.",
    )
    """
    Заголовок страницы. Отображается в интерфейсе и может использоваться в шаблонах.
    """

    slug = models.SlugField(
        unique=True,
        verbose_name="URL",
        help_text="Уникальный идентификатор страницы в URL (например, 'about-us').",
    )
    """
    Уникальный слаг для формирования читаемого URL страницы.
    Должен быть уникальным по всей системе.
    """

    content = HTMLField(
        verbose_name="Контент",
        default="<p>Контент сайта</p>",
        help_text="Основной контент страницы с поддержкой HTML-разметки.",
    )
    """
    Основное содержимое страницы с поддержкой HTML.
    Редактируется через визуальный редактор (например, CKEditor).
    """

    show_in_menu = models.BooleanField(
        default=True,
        verbose_name="Показывать в меню",
        help_text="Определите, будет ли страница отображаться в основном меню сайта.",
    )
    """
    Флаг отображения страницы в навигационном меню.
    """

    order = models.IntegerField(
        default=0,
        verbose_name="Порядок",
        help_text="Определяет порядок сортировки страниц в меню и списке.",
    )
    """
    Порядковый номер для сортировки страниц. Чем меньше значение — тем выше в списке.
    """

    logo = models.ImageField(
        upload_to=RenameUploadTo("page_logos/"),
        verbose_name="Логотип страницы",
        blank=True,
        null=True,
        help_text="Логотип, ассоциированный с данной страницей. Отображается в шапке или футере.",
    )
    """
    Изображение логотипа, привязанное к странице. Опционально.
    Загружается в папку 'page_logos/'.
    """

    fon_headers = models.ImageField(
        upload_to=RenameUploadTo("fon_headers/"),
        verbose_name="Фон шапки страницы",
        blank=True,
        null=True,
        help_text="Фон, ассоциированный с данной страницей. Отображается в шапке или футере.",
    )
    """
    Изображение фона шапки, привязанное к странице. Опционально.
    Загружается в папку 'fon_headers/'.
    """

    class Meta:
        """
        Метакласс для настройки поведения модели.

        Задаёт человекочитаемые названия для админ-панели и порядок сортировки объектов.
        """

        verbose_name = "Страница"
        verbose_name_plural = "Страницы"
        ordering = ["order", "title"]

    def __str__(self):
        """
        Возвращает строковое представление объекта страницы.

        Используется в админке Django и при отображении объекта в виде строки.

        Returns:
            str: Заголовок страницы.
        """
        return self.title
