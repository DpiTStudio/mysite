"""
Команда для синхронизации файлов логов с базой данных.
Использование: python manage.py sync_logs
"""
from django.core.management.base import BaseCommand
from logfiles.models import LogFile
import os
from pathlib import Path
from django.conf import settings


class Command(BaseCommand):
    help = 'Синхронизирует файлы логов с базой данных'

    def add_arguments(self, parser):
        parser.add_argument(
            '--log-dir',
            type=str,
            default=None,
            help='Путь к директории с логами (по умолчанию используется logs/)',
        )

    def handle(self, *args, **options):
        log_dir = options.get('log_dir')
        
        if log_dir:
            log_dir = Path(log_dir)
        else:
            log_dir = Path(settings.BASE_DIR) / "logs"
        
        if not log_dir.exists():
            self.stdout.write(
                self.style.WARNING(f'Директория {log_dir} не существует')
            )
            return
        
        self.stdout.write(f'Сканирование директории: {log_dir}')
        
        # Находим все .log файлы
        log_files = list(log_dir.glob('*.log'))
        
        if not log_files:
            self.stdout.write(
                self.style.WARNING('Лог-файлы не найдены')
            )
            return
        
        created_count = 0
        updated_count = 0
        
        for log_file_path in log_files:
            file_name = log_file_path.name
            file_path = str(log_file_path.absolute())
            
            # Проверяем, существует ли уже запись
            log_file, created = LogFile.objects.get_or_create(
                file_path=file_path,
                defaults={
                    'name': file_name,
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Создана запись для: {file_name}')
                )
            else:
                # Обновляем информацию о существующем файле
                if log_file.name != file_name:
                    log_file.name = file_name
                    log_file.save()
                log_file.update_file_info()
                updated_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Обновлена запись для: {file_name}')
                )
        
        # Удаляем записи о файлах, которых больше нет
        existing_paths = {str(Path(fp).absolute()) for fp in log_dir.glob('*.log')}
        for log_file in LogFile.objects.all():
            if log_file.file_path not in existing_paths:
                self.stdout.write(
                    self.style.WARNING(
                        f'Удалена запись о несуществующем файле: {log_file.name}'
                    )
                )
                log_file.delete()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nСинхронизация завершена. '
                f'Создано: {created_count}, Обновлено: {updated_count}'
            )
        )

