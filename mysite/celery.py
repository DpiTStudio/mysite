"""
Конфигурация Celery для проекта DPIT-CMS.
"""
import os
from celery import Celery

# Устанавливаем переменную окружения для настроек Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')

app = Celery('mysite')

# Читаем конфигурацию из настроек Django (ключи с префиксом CELERY_)
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматически обнаруживаем задачи во всех приложениях
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
