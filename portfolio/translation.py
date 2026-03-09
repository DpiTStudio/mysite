from modeltranslation.translator import register, TranslationOptions
from .models import Portfolio, PortfolioCategory

@register(PortfolioCategory)
class PortfolioCategoryTranslationOptions(TranslationOptions):
    fields = ('name', 'description', 'content')

@register(Portfolio)
class PortfolioTranslationOptions(TranslationOptions):
    fields = ('title', 'content')
