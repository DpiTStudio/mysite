from django import forms
from captcha.fields import CaptchaField, CaptchaTextInput

class ContactForm(forms.Form):
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
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+7 (___) ___-__-__'})
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Ваше сообщение'}),
        label="Сообщение"
    )
    captcha = CaptchaField(
        label="Введите текст с картинки",
        widget=CaptchaTextInput(attrs={'class': 'form-control mt-2', 'placeholder': 'Введите код с картинки'})
    )
