from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from captcha.fields import CaptchaField
from .models import User


class UserRegistrationForm(UserCreationForm):
    """Форма регистрации пользователя с капчей"""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "Email"})
    )
    phone = forms.CharField(
        required=False,
        max_length=20,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Телефон"})
    )
    captcha = CaptchaField(label="Капча")
    
    class Meta:
        model = User
        fields = ("username", "email", "phone", "password1", "password2")
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control", "placeholder": "Имя пользователя"}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password1"].widget.attrs.update({"class": "form-control", "placeholder": "Пароль"})
        self.fields["password2"].widget.attrs.update({"class": "form-control", "placeholder": "Подтверждение пароля"})


class UserLoginForm(AuthenticationForm):
    """Форма входа с капчей"""
    captcha = CaptchaField(label="Капча")
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update({"class": "form-control", "placeholder": "Имя пользователя"})
        self.fields["password"].widget.attrs.update({"class": "form-control", "placeholder": "Пароль"})


class UserProfileForm(forms.ModelForm):
    """Форма редактирования профиля"""
    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "phone", "avatar")
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "avatar": forms.FileInput(attrs={"class": "form-control"}),
        }
        labels = {
            "first_name": "Имя",
            "last_name": "Фамилия",
            "email": "Email",
            "phone": "Телефон",
            "avatar": "Аватар",
        }

