from modeltranslation.translator import register, TranslationOptions
from .models import News, NewsCategory, DailyEvent

@register(NewsCategory)
class NewsCategoryTranslationOptions(TranslationOptions):
    fields = ('name', 'description', 'content')

@register(News)
class NewsTranslationOptions(TranslationOptions):
    fields = ('title', 'content')

@register(DailyEvent)
class DailyEventTranslationOptions(TranslationOptions):
    fields = ('title', 'description')
