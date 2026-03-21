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
    """
    Форма оформления заказа.
    Для незарегистрированных пользователей показывает опцию авторегистрации.
    """

    auto_register = forms.BooleanField(
        required=False,
        initial=True,
        label="Создать личный кабинет автоматически",
        help_text="Мы автоматически создадим аккаунт и пришлём данные для входа на указанный email.",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'auto_register_check'}),
    )

    class Meta:
        model = Order
        fields = ['first_name', 'email', 'phone', 'comment']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ваше имя',
                'autocomplete': 'given-name',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ваш email (example@mail.com)',
                'autocomplete': 'email',
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+7 (___) ___-__-__',
                'inputmode': 'tel',
                'autocomplete': 'tel',
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Дополнительная информация о проекте или пожелания',
            }),
        }

    def clean_phone(self):
        return validate_phone(self.cleaned_data.get('phone', ''))

    def clean_email(self):
        return self.cleaned_data.get('email', '').strip().lower()
