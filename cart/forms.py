from django import forms
from .models import Order

class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'email', 'phone', 'company', 'comment']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ваше имя'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ваша фамилия (необязательно)'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Ваш email (example@mail.com)'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ваш телефон (+7(...))'}),
            'company': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Название компании (если есть)'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Дополнительная информация о проекте или пожелания'}),
        }
