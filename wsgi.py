"""
WSGI config for DPIT-CMS on NetAngels.

NetAngels запускает /home/c504113/dpit-cms.ru/app/wsgi.py и ожидает объект application.
Этот файл добавляет каталог приложения в sys.path и инициализирует Django WSGI application.
"""
import os
import sys
from pathlib import Path

# Корень Django-проекта (каталог с manage.py)
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
