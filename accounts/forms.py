"""
Модуль forms.py приложения accounts

Этот файл содержит Django-формы для обработки пользовательского ввода
при регистрации, входе в систему и редактировании профиля.

Формы обеспечивают:
- Валидацию данных на стороне сервера
- Защиту от спама через капчу
- Стилизацию полей для Bootstrap
- Автоматическую обработку паролей (хеширование, проверка совпадения)
"""

# Импорт базовых классов форм Django
from django import forms
# Импорт стандартных форм Django для регистрации и аутентификации
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
# Импорт поля капчи из библиотеки django-simple-captcha
from captcha.fields import CaptchaField
# Импорт кастомной модели пользователя
from .models import User


class UserRegistrationForm(UserCreationForm):
    """
    Форма регистрации нового пользователя.
    
    Наследуется от UserCreationForm, которая автоматически обрабатывает:
    - Создание пользователя
    - Хеширование пароля
    - Проверку совпадения паролей (password1 и password2)
    - Проверку сложности пароля
    
    Дополнительные поля:
    - email: Обязательное поле электронной почты
    - phone: Необязательное поле телефона
    - captcha: Поле капчи для защиты от автоматической регистрации ботов
    
    Все поля стилизованы для Bootstrap через CSS класс "form-control".
    """
    
    # Поле электронной почты
    # required=True: Поле обязательно для заполнения
    # widget: Виджет EmailInput с CSS классом и плейсхолдером для стилизации
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "Email"})
    )
    
    # Поле телефона
    # required=False: Поле необязательное
    # max_length=20: Максимальная длина строки (достаточно для международных форматов)
    phone = forms.CharField(
        required=False,
        max_length=20,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Телефон"})
    )
    
    # Поле капчи для защиты от автоматической регистрации
    # CaptchaField генерирует изображение с кодом, который нужно ввести
    # label: Подпись поля на русском языке
    captcha = CaptchaField(label="Капча")
    
    class Meta:
        """
        Класс Meta для настройки формы.
        
        Определяет модель, с которой связана форма, и поля, которые она содержит.
        """
        # Модель, с которой связана форма (User)
        model = User
        # Поля формы в порядке отображения:
        # username - имя пользователя
        # email - электронная почта
        # phone - телефон
        # password1 - пароль
        # password2 - подтверждение пароля
        fields = ("username", "email", "phone", "password1", "password2")
        # Настройка виджетов (HTML-элементов) для полей
        widgets = {
            # Виджет для поля username с CSS классом и плейсхолдером
            "username": forms.TextInput(attrs={"class": "form-control", "placeholder": "Имя пользователя"}),
        }
    
    def __init__(self, *args, **kwargs):
        """
        Инициализация формы.
        
        Переопределяет метод __init__ для добавления CSS классов и плейсхолдеров
        к полям паролей, которые наследуются от UserCreationForm.
        
        Args:
            *args: Позиционные аргументы
            **kwargs: Именованные аргументы
        """
        # Вызов родительского конструктора
        super().__init__(*args, **kwargs)
        
        # Добавление CSS классов и плейсхолдеров к полям паролей
        # Эти поля наследуются от UserCreationForm, поэтому их нужно настроить отдельно
        self.fields["password1"].widget.attrs.update({"class": "form-control", "placeholder": "Пароль"})
        self.fields["password2"].widget.attrs.update({"class": "form-control", "placeholder": "Подтверждение пароля"})


class UserLoginForm(AuthenticationForm):
    """
    Форма входа (авторизации) пользователя в систему.
    
    Наследуется от AuthenticationForm, которая автоматически обрабатывает:
    - Проверку существования пользователя с указанным username
    - Проверку правильности пароля
    - Активацию пользователя
    
    Дополнительное поле:
    - captcha: Поле капчи для защиты от брутфорса (подбора паролей)
    
    Все поля стилизованы для Bootstrap.
    """
    
    # Поле капчи для защиты от автоматического подбора паролей
    captcha = CaptchaField(label="Капча")
    
    def __init__(self, *args, **kwargs):
        """
        Инициализация формы.
        
        Добавляет CSS классы и плейсхолдеры к полям username и password
        для единообразной стилизации формы.
        
        Args:
            *args: Позиционные аргументы
            **kwargs: Именованные аргументы
        """
        # Вызов родительского конструктора
        super().__init__(*args, **kwargs)
        
        # Добавление CSS классов и плейсхолдеров к полям формы
        # Эти поля наследуются от AuthenticationForm
        self.fields["username"].widget.attrs.update({"class": "form-control", "placeholder": "Имя пользователя"})
        self.fields["password"].widget.attrs.update({"class": "form-control", "placeholder": "Пароль"})


class UserProfileForm(forms.ModelForm):
    """
    Форма редактирования профиля пользователя.
    
    Позволяет пользователю изменять свои личные данные:
    - Имя (first_name)
    - Фамилия (last_name)
    - Email
    - Телефон
    - Аватар (загрузка изображения)
    
    Не позволяет изменять:
    - Username (имя пользователя)
    - Пароль (для этого нужна отдельная форма смены пароля)
    - Права доступа (is_staff, is_superuser)
    """
    
    class Meta:
        """
        Класс Meta для настройки формы.
        
        Определяет модель и поля, доступные для редактирования.
        """
        # Модель, с которой связана форма
        model = User
        # Поля, которые можно редактировать через эту форму
        # Остальные поля (username, password и т.д.) недоступны для изменения
        fields = ("first_name", "last_name", "email", "phone", "avatar")
        
        # Настройка виджетов для всех полей
        # Все поля используют CSS класс "form-control" для стилизации Bootstrap
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            # FileInput для загрузки файла (аватара)
            "avatar": forms.FileInput(attrs={"class": "form-control"}),
        }
        
        # Человекочитаемые подписи полей на русском языке
        # Эти подписи отображаются в HTML-форме рядом с полями
        labels = {
            "first_name": "Имя",
            "last_name": "Фамилия",
            "email": "Email",
            "phone": "Телефон",
            "avatar": "Аватар",
        }

