from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Выполняет makemigrations и migrate'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Создание миграций...'))
        call_command('makemigrations')
        self.stdout.write(self.style.NOTICE('Применение миграций...'))
        call_command('migrate')
        self.stdout.write(self.style.SUCCESS('Готово!'))
