from django import forms
from captcha.fields import CaptchaField
from .models import Ticket, TicketMessage, TicketStatus, TicketPriority


class TicketForm(forms.ModelForm):
    """Форма создания тикета с капчей"""
    captcha = CaptchaField(label="Капча")
    
    class Meta:
        model = Ticket
        fields = ("subject", "description", "priority")
        widgets = {
            "subject": forms.TextInput(attrs={"class": "form-control", "placeholder": "Тема тикета"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 5, "placeholder": "Опишите вашу проблему"}),
            "priority": forms.Select(attrs={"class": "form-control"}),
        }
        labels = {
            "subject": "Тема",
            "description": "Описание",
            "priority": "Приоритет",
        }


class TicketMessageForm(forms.ModelForm):
    """Форма добавления сообщения в тикет"""
    class Meta:
        model = TicketMessage
        fields = ("message",)
        widgets = {
            "message": forms.Textarea(attrs={"class": "form-control", "rows": 4, "placeholder": "Ваше сообщение"}),
        }
        labels = {
            "message": "Сообщение",
        }

