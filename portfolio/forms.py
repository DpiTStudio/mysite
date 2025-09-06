from django import forms
from tinymce.widgets import TinyMCE
from .models import Portfolio, PortfolioCategory


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
