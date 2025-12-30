from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Ticket, TicketStatus
from .forms import TicketForm, TicketMessageForm


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
    
    context = {
        "tickets": tickets_page,
        "status_choices": TicketStatus.choices,
        "current_status": status_filter,
    }
    return render(request, "tickets/list.html", context)


@login_required
def ticket_create(request):
    """Создание нового тикета"""
    if request.method == "POST":
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.user = request.user
            ticket.save()
            messages.success(request, "Тикет успешно создан!")
            return redirect("tickets:detail", ticket_id=ticket.id)
    else:
        form = TicketForm()
    
    return render(request, "tickets/create.html", {"form": form})


@login_required
def ticket_detail(request, ticket_id):
    """Детальная страница тикета"""
    if request.user.is_staff:
        ticket = get_object_or_404(Ticket, id=ticket_id)
    else:
        ticket = get_object_or_404(Ticket, id=ticket_id, user=request.user)
    
    if request.method == "POST":
        form = TicketMessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.ticket = ticket
            message.user = request.user
            message.save()
            
            # Обновляем статус тикета, если он был закрыт
            if ticket.status == TicketStatus.CLOSED:
                ticket.status = TicketStatus.OPEN
                ticket.save()
            
            messages.success(request, "Сообщение добавлено!")
            return redirect("tickets:detail", ticket_id=ticket.id)
    else:
        form = TicketMessageForm()
    
    messages_list = ticket.messages.all()
    
    context = {
        "ticket": ticket,
        "messages": messages_list,
        "form": form,
    }
    return render(request, "tickets/detail.html", context)


@login_required
def ticket_close(request, ticket_id):
    """Закрытие тикета"""
    if request.user.is_staff:
        ticket = get_object_or_404(Ticket, id=ticket_id)
    else:
        ticket = get_object_or_404(Ticket, id=ticket_id, user=request.user)
    
    if ticket.status != TicketStatus.CLOSED:
        from django.utils import timezone
        ticket.status = TicketStatus.CLOSED
        ticket.closed_at = timezone.now()
        ticket.save()
        messages.success(request, "Тикет закрыт.")
    
    return redirect("tickets:detail", ticket_id=ticket.id)
