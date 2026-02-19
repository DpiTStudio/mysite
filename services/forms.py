# forms.py - Улучшенная версия
from django import forms
from tinymce.widgets import TinyMCE
from .models import ServiceOrder, Service, TECH_CHOICES

# Конфигурация TinyMCE для разных полей
tiny_config_basic = {
    'height': 300,
    'width': '100%',
    'menubar': False,
    'plugins': 'link image lists code',
    'toolbar': 'undo redo | formatselect | bold italic | '
              'alignleft aligncenter alignright | bullist numlist | '
              'link image | code',
}

tiny_config_advanced = {
    'height': 400,
    'width': '100%',
    'menubar': True,
    'plugins': [
        'advlist autolink lists link image charmap print preview anchor',
        'searchreplace visualblocks code fullscreen',
        'insertdatetime media table paste code help wordcount'
    ],
    'toolbar': 'undo redo | formatselect | bold italic backcolor | '
              'alignleft aligncenter alignright alignjustify | '
              'bullist numlist outdent indent | removeformat | '
              'link image media | code | help',
    'content_css': [
        '//fonts.googleapis.com/css?family=Lato:300,300i,400,400i',
        '//www.tiny.cloud/css/codepen.min.css'
    ]
}

tiny_config_seo = {
    'height': 150,
    'width': '100%',
    'menubar': False,
    'plugins': 'wordcount',
    'toolbar': 'undo redo | bold italic | wordcount',
    'max_chars': 160,
}

class ServiceAdminForm(forms.ModelForm):
    """
    Форма для управления услугами в административной панели.
    Включает расширенные поля выбора технологий и интеграцию с TinyMCE
    для визуального редактирования описаний.
    """
    technical_requirements = forms.MultipleChoiceField(
        choices=TECH_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Технические требования",
        help_text="Выберите технологии, используемые в услуге"
    )
    
    class Meta:
        model = Service
        fields = '__all__'
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'vTextField',
                'style': 'width: 300px; height: 20px; font-size: 14px; padding: 8px;'
            }),
            'slug': forms.TextInput(attrs={
                'class': 'vTextField',
                'style': 'width: 300px; height: 20px; font-size: 14px; padding: 8px;'
            }),
            # TinyMCE для HTML полей
            'short_description': TinyMCE(
                attrs={'cols': 80, 'rows': 10},
                mce_attrs=tiny_config_basic
            ),
            'description': TinyMCE(
                attrs={'cols': 80, 'rows': 20},
                mce_attrs=tiny_config_advanced
            ),
            'deliverables': TinyMCE(
                attrs={'cols': 80, 'rows': 10},
                mce_attrs=tiny_config_basic
            ),
            # SEO поля с TinyMCE для удобного редактирования
            'meta_description': TinyMCE(
                attrs={'cols': 80, 'rows': 4},
                mce_attrs=tiny_config_seo
            ),
            'meta_keywords': forms.Textarea(attrs={
                'rows': 3,
                'style': 'width: 300px; height: 20px; font-family: monospace;',
                'placeholder': 'Ключевые слова через запятую'
            }),
            'technical_requirements': forms.Textarea(attrs={
                'rows': 6,
                'style': 'width: 300px; height: 20px; font-family: monospace;',
                'placeholder': 'Или введите вручную через запятую'
            }),
            'icon': forms.FileInput(attrs={
                'class': 'vFileField',
                'style': 'padding: 8px;'
            }),
            'image': forms.FileInput(attrs={
                'class': 'vFileField',
                'style': 'padding: 8px;'
            }),
            'logo': forms.FileInput(attrs={
                'class': 'vFileField',
                'style': 'padding: 8px;'
            }),
            'price_min': forms.NumberInput(attrs={
                'style': 'width: 100px; height: 20px; text-align: left; padding: 1px;'
            }),
            'price_max': forms.NumberInput(attrs={
                'style': 'width: 100px; height: 20px; text-align: left; padding: 1px;'
            }),
            'price_fixed': forms.NumberInput(attrs={
                'style': 'width: 100px; height: 20px; text-align: left; padding: 1px;'
            }),
            'order': forms.NumberInput(attrs={
                'style': 'width: 80px; height: 20px; text-align: center; padding: 1px;'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        """Инициализация формы с загрузкой списка технологий"""
        super().__init__(*args, **kwargs)
        
        # Устанавливаем начальные значения для чекбоксов
        if self.instance and self.instance.technical_requirements:
            self.initial['technical_requirements'] = self.instance.get_tech_requirements_list()
        
        # Добавляем CSS классы для улучшения внешнего вида
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, (TinyMCE, forms.CheckboxSelectMultiple)):
                if 'class' not in field.widget.attrs:
                    field.widget.attrs['class'] = 'form-control'
    
    def save(self, commit=True):
        """Сохранение формы с преобразованием списка технологий в строку"""
        instance = super().save(commit=False)
        
        # Сохраняем выбранные значения как строку через запятую
        tech_requirements = self.cleaned_data.get('technical_requirements', [])
        if tech_requirements:
            instance.technical_requirements = ','.join(tech_requirements)
        else:
            instance.technical_requirements = ''
        
        if commit:
            instance.save()
        return instance


class ServiceOrderForm(forms.ModelForm):
    """
    Форма для оформления заказа на услугу клиентом.
    Включает контактную информацию и текст сообщения.
    """
    class Meta:
        model = ServiceOrder
        fields = ['full_name', 'phone', 'email', 'message']
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ваше имя',
                'style': 'padding: 10px; border-radius: 5px;'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+7 (XXX) XXX-XX-XX',
                'style': 'padding: 10px; border-radius: 5px;'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'email@example.com',
                'style': 'padding: 10px; border-radius: 5px;'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Опишите вашу задачу подробно...',
                'style': 'padding: 10px; border-radius: 5px; resize: vertical;'
            }),
        }
