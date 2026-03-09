from modeltranslation.translator import register, TranslationOptions
from .models import Page, SiteSettings

@register(Page)
class PageTranslationOptions(TranslationOptions):
    fields = ('title', 'content', 'meta_description', 'meta_keywords')

@register(SiteSettings)
class SiteSettingsTranslationOptions(TranslationOptions):
    fields = ('site_title', 'site_slogan', 'site_description', 'content', 'meta_title', 'meta_description', 'meta_keywords')
