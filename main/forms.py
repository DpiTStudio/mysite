"""
Модуль forms.py приложения main

Этот файл содержит Django-формы для обработки пользовательского ввода
на страницах сайта. В основном используется для формы обратной связи.
"""

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
    
    # Поле имени отправителя
    # max_length=100: Максимальная длина строки (достаточно для полного имени)
    # label: Подпись поля в HTML-форме
    # widget: Виджет TextInput с CSS классом и плейсхолдером для стилизации Bootstrap
    name = forms.CharField(
        max_length=100, 
        label="Ваше имя",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите ваше имя'})
    )
    
    # Поле электронной почты
    # EmailField автоматически валидирует формат email (должен содержать @ и домен)
    # widget: EmailInput - специальный виджет для email с валидацией на стороне браузера
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'example@mail.com'})
    )
    
    # Поле телефона
    # required=False: Поле необязательное для заполнения
    # max_length=20: Максимальная длина (достаточно для международных форматов)
    phone = forms.CharField(
        max_length=20, 
        label="Телефон",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+7 (___) ___-__-__'})
    )
    
    # Поле текста сообщения
    # widget: Textarea - многострочное текстовое поле
    # rows=4: Высота текстового поля (4 строки)
    message = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Ваше сообщение'}),
        label="Сообщение"
    )
    
    # Поле капчи для защиты от автоматических отправок
    # CaptchaField генерирует изображение с кодом, который нужно ввести
    # widget: CaptchaTextInput - виджет с полем для ввода кода
    # mt-2: CSS класс Bootstrap для отступа сверху (margin-top)
    captcha = CaptchaField(
        label="Введите текст с картинки",
        widget=CaptchaTextInput(attrs={'class': 'form-control mt-2', 'placeholder': 'Введите код с картинки'})
    )
