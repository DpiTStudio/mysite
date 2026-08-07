from django import forms
from tinymce.widgets import TinyMCE
from .models import News, NewsCategory, Comment


class NewsCategoryForm(forms.ModelForm):
    class Meta:
        model = NewsCategory
        fields = "__all__"
        widgets = {
            "description": TinyMCE(attrs={"cols": 80, "rows": 30}),
            "meta_title": forms.TextInput(
                attrs={
                    "class": "vTextField",
                    "placeholder": "Оптимально 50-60 символов...",
                    "style": "width: 100%; max-width: 800px;",
                }
            ),
            "meta_keywords": forms.TextInput(
                attrs={
                    "class": "vTextField",
                    "placeholder": "Ключевое слово 1, ключевое слово 2...",
                    "style": "width: 100%; max-width: 800px;",
                }
            ),
            "meta_description": forms.Textarea(
                attrs={
                    "class": "vLargeTextField",
                    "rows": 3,
                    "placeholder": "Краткое описание страницы для поисковых систем (рекомендуется 150-160 символов)...",
                    "style": "width: 100%; max-width: 800px;",
                }
            ),
        }


class NewsForm(forms.ModelForm):
    class Meta:
        model = News
        fields = "__all__"
        widgets = {
            "content": TinyMCE(attrs={"cols": 80, "rows": 30}),
            "meta_title": forms.TextInput(
                attrs={
                    "class": "vTextField",
                    "placeholder": "Оптимально 50-60 символов...",
                    "style": "width: 100%; max-width: 800px;",
                }
            ),
            "meta_keywords": forms.TextInput(
                attrs={
                    "class": "vTextField",
                    "placeholder": "Ключевое слово 1, ключевое слово 2...",
                    "style": "width: 100%; max-width: 800px;",
                }
            ),
            "meta_description": forms.Textarea(
                attrs={
                    "class": "vLargeTextField",
                    "rows": 3,
                    "placeholder": "Краткое описание страницы для поисковых систем (рекомендуется 150-160 символов)...",
                    "style": "width: 100%; max-width: 800px;",
                }
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
