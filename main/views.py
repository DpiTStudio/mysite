"""
Модуль views.py приложения main

Этот файл содержит представления (views) для обработки HTTP-запросов
на главной странице, статических страницах и обработчики ошибок.
"""

# Импорт функций для работы с шаблонами и перенаправлениями
from django.shortcuts import render, get_object_or_404, redirect
# Импорт моделей приложения main
from .models import Page, SiteSettings
# Импорт формы обратной связи
from .forms import ContactForm
# Импорт системы сообщений Django
from django.contrib import messages
# Импорт функции отправки email
from django.core.mail import send_mail
# Импорт настроек проекта
from django.conf import settings
# Импорт моделей из других приложений для статистики
from news.models import News, NewsCategory
from portfolio.models import Portfolio, PortfolioCategory
from reviews.models import Review
from tickets.models import Ticket
# Импорт функции для получения модели пользователя
from django.contrib.auth import get_user_model
# Импорт функции агрегации Sum для подсчета сумм
from django.db.models import Sum, Q

# Получение модели пользователя (может быть кастомная модель)
User = get_user_model()


def home(request):
    """
    Представление главной страницы сайта.
    
    Отображает главную страницу с различным контентом:
    - Герой-секция (через context processor или в шаблоне)
    - Популярные услуги
    - Последние работы портфолио
    - Свежие новости
    - Статистика для персонала
    """
    # Инициализация словаря статистики (пустой для обычных пользователей)
    stats = {}
    
    # Проверка, является ли пользователь персоналом (имеет доступ к админке)
    if request.user.is_staff:
        # Подсчет общего количества просмотров новостей
        news_views = News.objects.aggregate(total=Sum("views"))["total"] or 0
        # Подсчет общего количества просмотров портфолио
        portfolio_views = Portfolio.objects.aggregate(total=Sum("views"))["total"] or 0
        
        # Формирование словаря со статистикой
        stats = {
            "news_count": News.objects.count(),
            "news_categories_count": NewsCategory.objects.count(),
            "portfolio_count": Portfolio.objects.count(),
            "portfolio_categories_count": PortfolioCategory.objects.count(),
            "reviews_count": Review.objects.count(),
            "pending_reviews_count": Review.objects.filter(status="pending").count(),
            "tickets_count": Ticket.objects.count(),
            "open_tickets_count": Ticket.objects.filter(status="open").count(),
            "users_count": User.objects.count(),
            "total_views": news_views + portfolio_views,
        }

    # Получаем данные для динамических блоков
    from services.models import Service
    
    context = {
        "stats": stats,
        "popular_services": Service.objects.filter(is_active=True, is_popular=True)[:4],
        "latest_portfolio": Portfolio.objects.filter(is_active=True).order_by("-created_at")[:3],
        "recent_news": News.objects.filter(is_active=True).order_by("-created_at")[:3],
        "recent_reviews": Review.objects.filter(status="approved").order_by("-created_at")[:3],
    }
    
    return render(request, "main/home.html", context)


def global_search(request):
    """
    Универсальный поиск по всему сайту (Новости, Портфолио, Услуги).
    """
    query = request.GET.get("q", "").strip()
    results = {
        'news': [],
        'portfolio': [],
        'services': [],
        'total_count': 0
    }
    
    if query:
        from news.models import News
        from portfolio.models import Portfolio
        from services.models import Service
        
        results['news'] = News.objects.filter(
            is_active=True
        ).filter(
            Q(title__icontains=query) | Q(content__icontains=query) | Q(meta_description__icontains=query)
        ).select_related('category')[:5]
        
        results['portfolio'] = Portfolio.objects.filter(
            is_active=True
        ).filter(
            Q(title__icontains=query) | Q(content__icontains=query) | Q(meta_description__icontains=query)
        ).select_related('category')[:5]
        
        results['services'] = Service.objects.filter(
            is_active=True
        ).filter(
            Q(title__icontains=query) | Q(description__icontains=query) | Q(short_description__icontains=query)
        )[:5]
        
        results['total_count'] = (
            len(results['news']) + 
            len(results['portfolio']) + 
            len(results['services'])
        )

    return render(request, "main/search_results.html", {
        "query": query,
        "results": results
    })


def page_detail(request, slug):
    """
    Представление для отображения статической страницы.
    
    Отображает содержимое страницы по её slug (URL-идентификатору).
    Для страницы "kontakty" (контакты) дополнительно обрабатывает форму обратной связи.
    
    Логика работы:
    1. Получает страницу по slug из базы данных (404 если не найдена)
    2. Если slug = "kontakty" и запрос POST:
       - Валидирует форму обратной связи
       - Отправляет email администратору с данными формы
       - Выводит сообщение об успехе/ошибке
    3. Если slug = "kontakty" и запрос GET:
       - Отображает пустую форму обратной связи
    4. Рендерит шаблон страницы с контентом и формой (если применимо)
    
    Args:
        request: HTTP-запрос от клиента
        slug (str): URL-идентификатор страницы (например, "about", "kontakty")
    
    Returns:
        HttpResponse: HTML-страница с содержимым страницы
    """
    # Получение страницы из базы данных по slug
    # get_object_or_404: если страница не найдена, возвращает HTTP 404
    # is_active=True: только активные страницы
    page = get_object_or_404(Page, slug=slug, is_active=True)
    
    # Инициализация переменной для формы (None по умолчанию)
    form = None

    # Специальная обработка для страницы контактов
    if slug == "kontakty":
        # Обработка POST запроса (отправка формы обратной связи)
        if request.method == "POST":
            # Создание формы с данными из POST запроса
            form = ContactForm(request.POST)
            
            # Валидация формы
            if form.is_valid():
                # Получение настроек сайта для определения email получателя
                site_settings = SiteSettings.objects.filter(is_active=True).first()
                
                # Определение email получателя:
                # Если в настройках сайта указан email - используем его,
                # иначе используем email из настроек проекта
                recipient = site_settings.site_email if site_settings and site_settings.site_email else settings.EMAIL_HOST_USER
                
                # Формирование темы письма с именем отправителя
                subject = f"Сообщение с сайта: {form.cleaned_data['name']}"
                
                # Формирование текста письма с данными из формы
                # cleaned_data содержит валидированные данные формы
                message = f"""
                Имя: {form.cleaned_data['name']}
                Email: {form.cleaned_data['email']}
                Телефон: {form.cleaned_data['phone']}
                
                Сообщение:
                {form.cleaned_data['message']}
                """
                
                try:
                    # Отправка email через SMTP
                    # send_mail - функция Django для отправки почты
                    send_mail(
                        subject,                    # Тема письма
                        message,                    # Текст письма
                        settings.DEFAULT_FROM_EMAIL,  # Email отправителя
                        [recipient],                # Список получателей (список из одного адреса)
                        fail_silently=False,        # Не игнорировать ошибки (выбросить исключение)
                    )
                    
                    # Вывод сообщения об успешной отправке
                    messages.success(request, "Ваше сообщение успешно отправлено!")
                    
                    # Перенаправление на эту же страницу (PRG pattern)
                    return redirect("main:page_detail", slug=slug)
                except Exception as e:
                    # Обработка ошибок при отправке (например, проблемы с SMTP)
                    messages.error(request, f"Ошибка при отправке: {e}")
        else:
            # GET запрос: создание пустой формы для отображения
            form = ContactForm()

    # Рендеринг шаблона страницы
    # Передаем объект страницы и форму (если применимо) в контекст шаблона
    return render(request, "main/page_detail.html", {"page": page, "form": form})


def page_not_found(request, exception):
    """
    Обработчик ошибки 404 (страница не найдена).
    
    Вызывается Django автоматически, когда запрашиваемая страница не найдена.
    Используется только когда DEBUG=False в settings.py.
    
    Args:
        request: HTTP-запрос от клиента
        exception: Исключение, вызвавшее ошибку 404
    
    Returns:
        HttpResponse: HTML-страница с ошибкой 404 (статус код 404)
    """
    return render(request, "404.html", status=404)


def server_error(request):
    """
    Обработчик ошибки 500 (внутренняя ошибка сервера).
    
    Вызывается Django автоматически при возникновении необработанного исключения.
    Используется только когда DEBUG=False в settings.py.
    
    Args:
        request: HTTP-запрос от клиента
    
    Returns:
        HttpResponse: HTML-страница с ошибкой 500 (статус код 500)
    """
    return render(request, "500.html", status=500)


def robots_txt(request):
    """
    Генерация файла robots.txt динамически.
    
    Файл robots.txt используется поисковыми системами для определения,
    какие страницы сайта можно индексировать, а какие нет.
    
    Логика работы:
    1. Определяет протокол (http или https) в зависимости от режима DEBUG
    2. Получает хост из запроса
    3. Рендерит шаблон robots.txt с этими данными
    
    Args:
        request: HTTP-запрос от клиента
    
    Returns:
        HttpResponse: Текстовый файл robots.txt с правильным content_type
    """
    # Импорт настроек (локальный импорт для избежания циклических зависимостей)
    from django.conf import settings
    
    # Определение протокола:
    # Если DEBUG=False (production) - используем https
    # Если DEBUG=True (разработка) - используем http
    scheme = "https" if not settings.DEBUG else "http"
    
    # Получение хоста из запроса (например, "dpit-cms.ru" или "localhost:8000")
    host = request.get_host()
    
    # Рендеринг шаблона robots.txt
    # content_type="text/plain" указывает браузеру, что это текстовый файл
    return render(
        request,
        "robots.txt",
        {"scheme": scheme, "host": host},  # Передача данных в шаблон
        content_type="text/plain",  # MIME-тип ответа
    )
