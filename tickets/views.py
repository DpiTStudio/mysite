from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Ticket, TicketStatus, TicketMessage
from .forms import TicketForm, TicketMessageForm


# Создание представлений для управления тикетами поддержки
@login_required
def ticket_list(request):
    """Список тикетов пользователя (для персонала — все тикеты)"""
    if request.user.is_staff:
        tickets = Ticket.objects.all()
    else:
        tickets = Ticket.objects.filter(user=request.user)
    
    # Фильтрация по статусу
    status_filter = request.GET.get("status")
    if status_filter:
        tickets = tickets.filter(status=status_filter)
    
    # Пагинация
    paginator = Paginator(tickets, 10)
    page = request.GET.get("page")
    tickets_page = paginator.get_page(page)
    
    # Контекст для шаблона
    context = {
        "tickets": tickets_page,
        "status_choices": TicketStatus.choices,
        "current_status": status_filter,
    }
    return render(request, "tickets/list.html", context)


# Создание нового тикета
@login_required
def ticket_create(request): 
    """Создание нового тикета"""
    if request.method == "POST": # Обработка отправки формы
        form = TicketForm(request.POST) # Инициализация формы с данными из запроса
        if form.is_valid(): # Проверка валидности формы
            ticket = form.save(commit=False) # Создание объекта тикета без сохранения в БД
            ticket.user = request.user # Привязка тикета к текущему пользователю
            ticket.save() # Сохранение тикета в БД
            messages.success(request, "Тикет успешно создан!") # Сообщение об успешном создании
            return redirect("tickets:detail", ticket_id=ticket.pk) # Перенаправление на страницу детального просмотра тикета
    else: # Обработка GET-запроса
        form = TicketForm() # Инициализация пустой формы

    # Рендеринг шаблона с формой
    return render(request, "tickets/create.html", {"form": form})


@login_required
def ticket_detail(request, ticket_id):
    """Детальная страница тикета"""
    if request.user.is_staff: # Получение тикета для персонала
        ticket = get_object_or_404(Ticket, id=ticket_id) # Получение тикета по ID
    else: # Получение тикета для обычного пользователя
        ticket = get_object_or_404(Ticket, id=ticket_id, user=request.user)
    
    if request.method == "POST": # Обработка отправки нового сообщения
        form = TicketMessageForm(request.POST) # Инициализация формы с данными из запроса
        if form.is_valid(): # Проверка валидности формы
            message = form.save(commit=False)   # Создание объекта сообщения без сохранения в БД
            message.ticket = ticket # Привязка сообщения к тикету
            message.user = request.user # Привязка сообщения к текущему пользователю
            message.save()  # Сохранение сообщения в БД
            
            # Обновляем статус тикета, если он был закрыт
            if ticket.status == TicketStatus.CLOSED: # Если тикет был закрыт
                ticket.status = TicketStatus.OPEN # Меняем статус на открытый
                ticket.save() # Сохранение изменений в БД
            
            messages.success(request, "Сообщение добавлено!") # Сообщение об успешном добавлении
            return redirect("tickets:detail", ticket_id=ticket.pk) # Перенаправление на страницу детального просмотра тикета
    else:
        form = TicketMessageForm() # Инициализация пустой формы для нового сообщения
    
    # Получение всех сообщений тикета через модель TicketMessage (без обращения к related_name, чтобы избежать ошибок типизатора)
    messages_list = TicketMessage.objects.filter(ticket=ticket).order_by("created_at")
    
    # Контекст для шаблона
    context = {
        "ticket": ticket, # Текущий тикет
        "messages": messages_list, # Сообщения тикета
        "form": form, # Форма для нового сообщения
    }

    # Рендеринг шаблона с деталями тикета
    return render(request, "tickets/detail.html", context)


# Закрытие тикета
@login_required
def ticket_close(request, ticket_id):
    """Закрытие тикета"""
    # Получаем тикет: сотрудник может закрыть любой тикет, обычный пользователь — только свой
    if request.user.is_staff:
        ticket = get_object_or_404(Ticket, id=ticket_id)
    else:
        ticket = get_object_or_404(Ticket, id=ticket_id, user=request.user)

    # Проверка прав: сотрудник или владелец могут закрыть тикет
    if request.user.is_staff or request.user == ticket.user:
        if ticket.status != TicketStatus.CLOSED:
            from django.utils import timezone  # Импорт модуля для работы с временем
            ticket.status = TicketStatus.CLOSED  # Обновление статуса тикета на закрытый
            ticket.closed_at = timezone.now()  # Установка времени закрытия тикета
            ticket.save()  # Сохранение изменений в БД
            messages.success(request, "Тикет закрыт.")  # Сообщение об успешном закрытии тикета
        else:
            messages.warning(request, "Тикет уже закрыт.")  # Сообщение, если тикет уже закрыт
    else:
        messages.error(request, "У вас нет прав для закрытия этого тикета.")  # Сообщение об ошибке, если пользователь не сотрудник

    # Перенаправление на страницу детального просмотра тикета
    return redirect("tickets:detail", ticket_id=ticket.pk)
