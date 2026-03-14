"""
Модуль forms.py приложения main

Этот файл содержит Django-формы для обработки пользовательского ввода
на страницах сайта. В основном используется для формы обратной связи.
"""

import re
# Импорт базовых классов форм Django
from django import forms
# Импорт поля капчи и виджета для защиты от спама
from captcha.fields import CaptchaField, CaptchaTextInput


class ContactForm(forms.Form):
    """
    Форма обратной связи для страницы контактов.

    Позволяет посетителям сайта отправить сообщение администратору.
    Все поля стилизованы для Bootstrap через CSS класс "form-control".
    Форма защищена капчей для предотвращения автоматических спам-рассылок.

    Поля формы:
    - name: Имя отправителя (обязательное)
    - email: Электронная почта для ответа (обязательное)
    - phone: Телефон (необязательное)
    - message: Текст сообщения (обязательное)
    - captcha: Поле капчи для защиты от ботов (обязательное)
    """

    name = forms.CharField(
        max_length=100,
        label="Ваше имя",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите ваше имя'})
    )

    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'example@mail.com'})
    )

    phone = forms.CharField(
        max_length=20,
        label="Телефон",
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+7 (___) ___-__-__',
            'inputmode': 'tel',
        })
    )

    message = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Ваше сообщение'}),
        label="Сообщение"
    )

    captcha = CaptchaField(
        label="Введите текст с картинки",
        widget=CaptchaTextInput(attrs={'class': 'form-control mt-2', 'placeholder': 'Введите код с картинки'})
    )

    def clean_phone(self):
        """
        Валидация и нормализация номера телефона.

        - Поле необязательное: пустое значение разрешено.
        - Разрешает только цифры, +, (, ), -, пробел.
        - Проверяет: минимум 10 и максимум 15 цифр.
        """
        phone = self.cleaned_data.get('phone', '').strip()
        if not phone:
            return phone  # Необязательное поле — пустое значение ОК

        # Проверка допустимых символов
        if not re.match(r'^[\d\+\(\)\-\s]+$', phone):
            raise forms.ValidationError(
                "Номер телефона может содержать только цифры, +, (, ), — и пробел."
            )

        # Количество цифр
        digits_only = re.sub(r'\D', '', phone)
        if len(digits_only) < 10:
            raise forms.ValidationError(
                "Введите корректный номер телефона (не менее 10 цифр)."
            )
        if len(digits_only) > 15:
            raise forms.ValidationError(
                "Номер телефона слишком длинный (не более 15 цифр)."
            )

        return phone
