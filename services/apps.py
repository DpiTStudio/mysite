from django.apps import AppConfig

class ServicesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'services'
    verbose_name = 'Услуги'

    def ready(self):
        # Импортируем и регистрируем сигналы
        import services.signals