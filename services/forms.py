from django import forms
from django.utils.translation import gettext_lazy as _
from .models import ServiceOrder

class ServiceOrderForm(forms.ModelForm):
    class Meta:
        model = ServiceOrder
        fields = ['full_name', 'phone', 'email', 'message', 'estimated_budget', 'deadline']
        widgets = {
            'full_name': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': _('Иванов Иван')}
            ),
            'phone': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': '+7 (999) 000-00-00'}
            ),
            'email': forms.EmailInput(
                attrs={'class': 'form-control', 'placeholder': 'example@mail.ru'}
            ),
            'message': forms.Textarea(
                attrs={
                    'class': 'form-control', 
                    'rows': 4, 
                    'placeholder': _('Опишите вашу задачу и пожелания...')
                }
            ),
            'estimated_budget': forms.NumberInput(
                attrs={'class': 'form-control', 'placeholder': _('Примерный бюджет (руб)')}
            ),
            'deadline': forms.DateInput(
                attrs={'class': 'form-control', 'type': 'date'}
            ),
        }
