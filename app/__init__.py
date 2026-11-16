# Подгружаем PyMySQL как MySQLdb для работы с MySQL без компиляции C-библиотек
import pymysql

pymysql.install_as_MySQLdb()

# Подгружаем Celery при старте Django
from .celery import app as celery_app

__all__ = ('celery_app',)
