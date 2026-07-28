from django import forms
from django.utils.translation import gettext_lazy as _
from .models import ServiceOrder

class ServiceOrderForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'selected_plan' in self.fields:
            self.fields['selected_plan'].empty_label = _("— Без выбора тарифа —")
            self.fields['selected_plan'].label = _("Тарифный план")

    class Meta:
        model = ServiceOrder
        fields = ['full_name', 'phone', 'email', 'selected_plan', 'message', 'estimated_budget', 'deadline']
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
            'selected_plan': forms.Select(
                attrs={'class': 'form-select', 'id': 'id_selected_plan'}
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

    def clean_selected_plan(self):
        plan = self.cleaned_data.get('selected_plan')
        if plan and not plan.is_available_for_order:
            raise forms.ValidationError(_("Выбранный тарифный план в данный момент недоступен для заказа."))
        return plan

