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
    site_title = models.CharField(max_length=200, verbose_name="Название сайта")
    site_slogan = models.CharField(max_length=30, verbose_name="Слоган")
    site_description = models.TextField(max_length=255, verbose_name="Описание сайта")
    site_email = models.EmailField(max_length=30, verbose_name="Электронная почта")
    site_phone_1 = models.CharField(max_length=20, verbose_name="Телефон 1")
    site_phone_2 = models.CharField(max_length=20, verbose_name="Телефон 2")
    site_address = models.CharField(max_length=200, verbose_name="Адрес")
    content = HTMLField(verbose_name="Контент", default="<p>Контент сайта</p>")
    logo = models.ImageField(upload_to=RenameUploadTo("logos/"), verbose_name="Логотип")
    favicon = models.ImageField(upload_to=RenameUploadTo("favicons/"), verbose_name="Фавикон")
    fon_haeders = models.ImageField(upload_to=RenameUploadTo("fon_haeders/"), verbose_name="Фон шапки")
    site_domain = models.CharField(
        max_length=200,
        verbose_name="Домен сайта",
        blank=True,
        null=True,
        help_text="Домен сайта для отображения в шапке (например, dpit-cms.ru). Если не указан, будет использоваться текущий хост.",
    )
    site_work_time = models.CharField(
        max_length=200, 
        verbose_name="Время работы",
        blank=True,
        null=True,
        help_text="Время работы компании (например: Пн-Пт: 9:00-18:00)"
    )
    # Социальные сети (ссылки и иконки)
    site_vk = models.CharField(
        max_length=200,
        verbose_name="VK",
        blank=True,
        help_text="Ссылка на социальную сеть ВК"
    )
    site_vk_img = models.ImageField(
        upload_to=RenameUploadTo("social/vk/"),
        verbose_name="VK иконка",
        blank=True,
        null=True,
        help_text="Изображение иконки для социальной сети ВКонтакте"
    )
    site_ok = models.CharField(
        max_length=200,
        verbose_name="OK",
        blank=True,
        help_text="Ссылка на социальную сеть OK"
    )
    site_ok_img = models.ImageField(
        upload_to=RenameUploadTo("social/ok/"),
        verbose_name="OK иконка",
        blank=True,
        null=True,
        help_text="Изображение иконки для социальной сети Одноклассники"
    )
    site_facebook = models.CharField(
        max_length=200,
        verbose_name="FaceBook",
        blank=True,
        help_text="Ссылка на социальную сеть FaceBook"
    )
    site_facebook_img = models.ImageField(
        upload_to=RenameUploadTo("social/facebook/"),
        verbose_name="FaceBook иконка",
        blank=True,
        null=True,
        help_text="Изображение иконки для социальной сети Facebook"
    )
    site_linkedin = models.CharField(
        max_length=200,
        verbose_name="Linkedin",
        blank=True,
        help_text="Ссылка на социальную сеть Linkedin"
    )
    site_linkedin_img = models.ImageField(
        upload_to=RenameUploadTo("social/linkedin/"),
        verbose_name="Linkedin иконка",
        blank=True,
        null=True,
        help_text="Изображение иконки для социальной сети LinkedIn"
    )
    site_instagram = models.CharField(
        max_length=200,
        verbose_name="Instagram",
        blank=True,
        help_text="Ссылка на социальную сеть Instagram"
    )
    site_instagram_img = models.ImageField(
        upload_to=RenameUploadTo("social/instagram/"),
        verbose_name="Instagram иконка",
        blank=True,
        null=True,
        help_text="Изображение иконки для социальной сети Instagram"
    )
    site_twitter = models.CharField(
        max_length=200,
        verbose_name="Twitter",
        blank=True,
        help_text="Ссылка на социальную сеть Twitter"
    )
    site_twitter_img = models.ImageField(
        upload_to=RenameUploadTo("social/twitter/"),
        verbose_name="Twitter иконка",
        blank=True,
        null=True,
        help_text="Изображение иконки для социальной сети Twitter"
    )
    site_telegram = models.CharField(
        max_length=200,
        verbose_name="Telegram",
        blank=True,
        help_text="Ссылка на социальную сеть Telegram"
    )
    site_telegram_img = models.ImageField(
        upload_to=RenameUploadTo("social/telegram/"),
        verbose_name="Telegram иконка",
        blank=True,
        null=True,
        help_text="Изображение иконки для социальной сети Telegram"
    )
    site_whatsapp = models.CharField(
        max_length=200,
        verbose_name="Whatsapp",
        blank=True,
        help_text="Ссылка на социальную сеть Whatsapp"
    )
    site_whatsapp_img = models.ImageField(
        upload_to=RenameUploadTo("social/whatsapp/"),
        verbose_name="Whatsapp иконка",
        blank=True,
        null=True,
        help_text="Изображение иконки для социальной сети WhatsApp"
    )
    site_youtube = models.CharField(
        max_length=200,
        verbose_name="Youtube",
        blank=True,
        help_text="Ссылка на социальную сеть Youtube"
    )
    site_youtube_img = models.ImageField(
        upload_to=RenameUploadTo("social/youtube/"),
        verbose_name="Youtube иконка",
        blank=True,
        null=True,
        help_text="Изображение иконки для социальной сети YouTube"
    )

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