from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class TicketStatus(models.TextChoices):
    OPEN = "open", _("Открыт")
    IN_PROGRESS = "in_progress", _("В работе")
    RESOLVED = "resolved", _("Решен")
    CLOSED = "closed", _("Закрыт")


class TicketPriority(models.TextChoices):
    LOW = "low", _("Низкий")
    MEDIUM = "medium", _("Средний")
    HIGH = "high", _("Высокий")
    URGENT = "urgent", _("Срочный")


class Ticket(models.Model):
    """Модель тикета"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tickets", verbose_name="Пользователь")
    subject = models.CharField(max_length=200, verbose_name="Тема")
    description = models.TextField(verbose_name="Описание")
    status = models.CharField(
        max_length=20,
        choices=TicketStatus.choices,
        default=TicketStatus.OPEN,
        verbose_name="Статус"
    )
    priority = models.CharField(
        max_length=20,
        choices=TicketPriority.choices,
        default=TicketPriority.MEDIUM,
        verbose_name="Приоритет"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создан")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлен")
    closed_at = models.DateTimeField(null=True, blank=True, verbose_name="Закрыт")
    
    class Meta:
        verbose_name = "Тикет"
        verbose_name_plural = "Тикеты"
        ordering = ["-created_at"]
    
    def __str__(self):
        return f"{self.subject} ({self.get_status_display()})"


class TicketMessage(models.Model):
    """Модель сообщения в тикете"""
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name="messages", verbose_name="Тикет")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Автор")
    message = models.TextField(verbose_name="Сообщение")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    is_internal = models.BooleanField(default=False, verbose_name="Внутреннее сообщение")
    
    class Meta:
        verbose_name = "Сообщение тикета"
        verbose_name_plural = "Сообщения тикетов"
        ordering = ["created_at"]
    
    def __str__(self):
        return f"Сообщение в тикете #{self.ticket.id}"
