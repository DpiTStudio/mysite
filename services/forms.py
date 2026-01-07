from django import forms
from .models import ServiceOrder, Service, TECH_CHOICES

class ServiceAdminForm(forms.ModelForm):
    technical_requirements = forms.MultipleChoiceField(
        choices=TECH_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Технические условия",
        help_text="Языки, особенности и т.д."
    )
    
    class Meta:
        model = Service
        fields = '__all__'
        widgets = {
            'title': forms.TextInput(attrs={'style': 'width: 600px;'}),
            'slug': forms.TextInput(attrs={'style': 'width: 400px;'}),
            'short_description': forms.Textarea(attrs={'rows': 3, 'style': 'width: 800px;'}),
            'description': forms.Textarea(attrs={'rows': 10, 'style': 'width: 800px;'}),
            'technical_requirements': forms.Textarea(attrs={'rows': 6, 'style': 'width: 800px;'}),
            'meta_description': forms.Textarea(attrs={'rows': 3, 'style': 'width: 800px;'}),
            'meta_keywords': forms.Textarea(attrs={'rows': 3, 'style': 'width: 800px;'}),
            'icon': forms.FileInput(attrs={'style': 'width: 400px;'}),
            'image': forms.FileInput(attrs={'style': 'width: 400px;'}),
            'logo': forms.FileInput(attrs={'style': 'width: 400px;'}),
            'price_min': forms.NumberInput(attrs={'style': 'width: 100px;'}),
            'price_max': forms.NumberInput(attrs={'style': 'width: 100px;'}),
            'price': forms.NumberInput(attrs={'style': 'width: 100px;'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Устанавливаем начальные значения для чекбоксов
        if self.instance and self.instance.technical_requirements:
            self.initial['technical_requirements'] = self.instance.get_tech_requirements_list()
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Сохраняем выбранные значения как строку через запятую
        tech_requirements = self.cleaned_data.get('technical_requirements', [])
        instance.technical_requirements = ','.join(tech_requirements)
        
        if commit:
            instance.save()
        return instance


class ServiceOrderForm(forms.ModelForm):
    class Meta:
        model = ServiceOrder
        fields = ['full_name', 'phone', 'email', 'message']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ваше имя'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Телефон'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Комментарий к заказу'}),
        }