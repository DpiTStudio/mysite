from modeltranslation.translator import register, TranslationOptions
from .models import Service, Technology

@register(Technology)
class TechnologyTranslationOptions(TranslationOptions):
    fields = ('name',)

@register(Service)
class ServiceTranslationOptions(TranslationOptions):
    fields = ('title', 'short_description', 'description', 'deliverables', 'estimated_time', 'category')
