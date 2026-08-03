from django import forms
from tinymce.widgets import TinyMCE
from .models import News, NewsCategory, Comment


class NewsCategoryForm(forms.ModelForm):
    class Meta:
        model = NewsCategory
        fields = "__all__"
        widgets = {
            "description": TinyMCE(attrs={"cols": 80, "rows": 30}),
        }


class NewsForm(forms.ModelForm):
    class Meta:
        model = News
        fields = "__all__"
        widgets = {
            "content": TinyMCE(attrs={"cols": 80, "rows": 30}),
            "meta_description": forms.Textarea(
                attrs={"cols": 80, "rows": 4, "class": "vLargeTextField"}
            ),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["rating", "text"]
        labels = {
            "rating": "Оценка (от 1 до 5 звезд)",
            "text": "Ваш комментарий",
        }
        widgets = {
            "rating": forms.NumberInput(
                attrs={
                    "class": "form-control news-search-input py-2 shadow-none",
                    "min": 1,
                    "max": 5,
                    "value": 5,
                }
            ),
            "text": forms.Textarea(
                attrs={
                    "class": "form-control news-search-input p-3 shadow-none",
                    "rows": 3,
                    "placeholder": "Поделитесь вашим мнением или отзывом о публикации...",
                    "style": "border-radius: 16px;",
                }
            ),
        }
