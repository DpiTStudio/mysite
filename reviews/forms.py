from django import forms
from captcha.fields import CaptchaField
from .models import Review


class ReviewForm(forms.ModelForm):
    captcha = CaptchaField(label="Капча")
    
    class Meta:
        model = Review
        fields = ["full_name", "phone", "email", "content"]
        widgets = {
            "full_name": forms.TextInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "content": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
        }
        labels = {
            "full_name": "ФИО",
            "phone": "Телефон",
            "email": "Email",
            "content": "Текст отзыва",
        }
