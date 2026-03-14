"""
Celery-задачи для автоматического резервного копирования.

Включает:
- backup_database: бэкап SQLite (или pg_dump для PostgreSQL)
- backup_media: архивация медиа-файлов
- cleanup_old_backups: удаление старых бэкапов

Настройка расписания Celery Beat:
    см. mysite/settings.py -> CELERY_BEAT_SCHEDULE
"""

import os
import shutil
import logging
from datetime import datetime
from pathlib import Path

from celery import shared_task
from django.conf import settings

logger = logging.getLogger(__name__)

# Директория для бэкапов
BACKUP_ROOT = Path(settings.BASE_DIR) / 'backups'
DB_BACKUP_DIR = BACKUP_ROOT / 'database'
MEDIA_BACKUP_DIR = BACKUP_ROOT / 'media'

# Максимальное количество бэкапов каждого типа (старые удаляются)
MAX_DB_BACKUPS = getattr(settings, 'BACKUP_MAX_DB_COUNT', 14)
MAX_MEDIA_BACKUPS = getattr(settings, 'BACKUP_MAX_MEDIA_COUNT', 7)


def _ensure_dirs():
    """Создаёт директории для бэкапов если они не существуют."""
    DB_BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    MEDIA_BACKUP_DIR.mkdir(parents=True, exist_ok=True)


@shared_task(name='backup.database', bind=True, max_retries=2)
def backup_database(self):
    """
    Создаёт бэкап базы данных.
    
    - SQLite: копирует файл .db
    - PostgreSQL: использует pg_dump
    
    Возвращает путь к созданному файлу бэкапа.
    """
    _ensure_dirs()
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    db_config = settings.DATABASES.get('default', {})
    engine = db_config.get('ENGINE', '')
    
    try:
        if 'sqlite3' in engine:
            db_path = Path(db_config['NAME'])
            if not db_path.exists():
                logger.warning(f'[Backup] SQLite файл не найден: {db_path}')
                return None
            
            backup_filename = f'db_sqlite_{timestamp}.sqlite3'
            backup_path = DB_BACKUP_DIR / backup_filename
            shutil.copy2(str(db_path), str(backup_path))
            
            size_mb = backup_path.stat().st_size / 1024 / 1024
            logger.info(f'[Backup] SQLite бэкап создан: {backup_filename} ({size_mb:.2f} MB)')
            return str(backup_path)

        elif 'postgresql' in engine or 'psycopg2' in engine:
            import subprocess
            backup_filename = f'db_postgres_{timestamp}.sql'
            backup_path = DB_BACKUP_DIR / backup_filename
            
            env = os.environ.copy()
            if db_config.get('PASSWORD'):
                env['PGPASSWORD'] = db_config['PASSWORD']
            
            cmd = [
                'pg_dump',
                '-h', db_config.get('HOST', 'localhost'),
                '-p', str(db_config.get('PORT', 5432)),
                '-U', db_config.get('USER', 'postgres'),
                '-d', db_config.get('NAME', 'dpit_cms'),
                '-f', str(backup_path),
                '--no-password',
            ]
            result = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=120)
            
            if result.returncode != 0:
                logger.error(f'[Backup] pg_dump ошибка: {result.stderr}')
                raise Exception(f'pg_dump failed: {result.stderr}')
            
            size_mb = backup_path.stat().st_size / 1024 / 1024
            logger.info(f'[Backup] PostgreSQL бэкап создан: {backup_filename} ({size_mb:.2f} MB)')
            return str(backup_path)
        
        else:
            logger.warning(f'[Backup] Неподдерживаемый движок БД: {engine}')
            return None

    except Exception as exc:
        logger.exception(f'[Backup] Ошибка создания бэкапа БД: {exc}')
        raise self.retry(exc=exc, countdown=60)


@shared_task(name='backup.media', bind=True, max_retries=2)
def backup_media(self):
    """
    Архивирует папку media/ в ZIP-файл.
    
    Возвращает путь к созданному архиву.
    """
    _ensure_dirs()
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    media_root = Path(settings.MEDIA_ROOT)
    if not media_root.exists():
        logger.warning('[Backup] MEDIA_ROOT не существует, пропускаем.')
        return None
    
    backup_filename = f'media_{timestamp}'
    backup_path = MEDIA_BACKUP_DIR / backup_filename
    
    try:
        archive_path = shutil.make_archive(
            base_name=str(backup_path),
            format='zip',
            root_dir=str(media_root.parent),
            base_dir=media_root.name,
        )
        size_mb = Path(archive_path).stat().st_size / 1024 / 1024
        logger.info(f'[Backup] Media архив создан: {backup_filename}.zip ({size_mb:.2f} MB)')
        return archive_path

    except Exception as exc:
        logger.exception(f'[Backup] Ошибка архивации media: {exc}')
        raise self.retry(exc=exc, countdown=60)


@shared_task(name='backup.cleanup')
def cleanup_old_backups():
    """
    Удаляет старые бэкапы, оставляя максимум MAX_DB_BACKUPS бэкапов БД
    и MAX_MEDIA_BACKUPS бэкапов медиа.
    
    Сортирует по дате создания (новые — в конце).
    """
    deleted_count = 0

    def _cleanup_dir(directory: Path, max_count: int, pattern: str = '*'):
        nonlocal deleted_count
        if not directory.exists():
            return
        files = sorted(directory.glob(pattern), key=lambda f: f.stat().st_mtime)
        to_delete = files[:-max_count] if len(files) > max_count else []
        for f in to_delete:
            try:
                f.unlink()
                deleted_count += 1
                logger.info(f'[Backup Cleanup] Удалён старый бэкап: {f.name}')
            except OSError as e:
                logger.warning(f'[Backup Cleanup] Не удалось удалить {f}: {e}')

    _cleanup_dir(DB_BACKUP_DIR, MAX_DB_BACKUPS)
    _cleanup_dir(MEDIA_BACKUP_DIR, MAX_MEDIA_BACKUPS)

    logger.info(f'[Backup Cleanup] Завершено. Удалено файлов: {deleted_count}')
    return deleted_count


@shared_task(name='backup.full')
def full_backup():
    """Создаёт полный бэкап: БД + медиа, затем очищает старые."""
    logger.info('[Backup] Запуск полного бэкапа...')
    db_result = backup_database.delay()
    media_result = backup_media.delay()
    cleanup_old_backups.apply_async(countdown=30)  # Очистка через 30 сек после бэкапов
    return {
        'db_task_id': str(db_result.id),
        'media_task_id': str(media_result.id),
    }
