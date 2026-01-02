from django import forms
from tinymce.widgets import TinyMCE
from .models import Portfolio, PortfolioCategory, ServiceOrder


class PortfolioCategoryForm(forms.ModelForm):
    class Meta:
        model = PortfolioCategory
        fields = "__all__"
        widgets = {
            "description": TinyMCE(attrs={"cols": 80, "rows": 30}),
        }


class PortfolioForm(forms.ModelForm):
    class Meta:
        model = Portfolio
        fields = "__all__"
        widgets = {
            "content": TinyMCE(attrs={"cols": 80, "rows": 30}),
            "meta_description": TinyMCE(attrs={"cols": 80, "rows": 30}),
        }


class ServiceOrderForm(forms.ModelForm):
    class Meta:
        model = ServiceOrder
        fields = ["full_name", "email", "phone", "message"]
        widgets = {
            "full_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ваше ФИО"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "Email"}),
            "phone": forms.TextInput(attrs={"class": "form-control", "placeholder": "Телефон"}),
            "message": forms.Textarea(attrs={"class": "form-control", "placeholder": "Ваше сообщение", "rows": 4}),
        }

