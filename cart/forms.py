import re
from django import forms
from .models import Order


def validate_phone(value):
    """
    Общий валидатор номера телефона.
    Разрешает цифры, +, (, ), -, пробел.
    Требует от 10 до 15 цифр.
    """
    if not value:
        return value
    value = value.strip()
    if not re.match(r'^[\d\+\(\)\-\s]+$', value):
        raise forms.ValidationError(
            "Номер может содержать только цифры, +, (, ), — и пробел."
        )
    digits = re.sub(r'\D', '', value)
    if len(digits) < 10:
        raise forms.ValidationError("Введите корректный номер телефона (мин. 10 цифр).")
    if len(digits) > 15:
        raise forms.ValidationError("Номер телефона слишком длинный (макс. 15 цифр).")
    return value


class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'email', 'phone', 'company', 'comment']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ваше имя'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ваша фамилия (необязательно)'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Ваш email (example@mail.com)'}),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+7 (___) ___-__-__',
                'inputmode': 'tel',
            }),
            'company': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Название компании (если есть)'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Дополнительная информация о проекте или пожелания'}),
        }

    def clean_phone(self):
        return validate_phone(self.cleaned_data.get('phone', ''))
