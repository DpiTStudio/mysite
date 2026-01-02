from django.db import models
from main.utils import RenameUploadTo
import os


class LogFile(models.Model):
    """
    Модель для представления файла лога.
    """
    name = models.CharField(
        max_length=255,
        verbose_name="Название файла",
        help_text="Имя файла лога"
    )
    file_path = models.CharField(
        max_length=500,
        verbose_name="Путь к файлу",
        help_text="Полный путь к файлу лога"
    )
    size = models.BigIntegerField(
        default=0,
        verbose_name="Размер (байт)",
        help_text="Размер файла в байтах"
    )
    last_modified = models.DateTimeField(
        auto_now=True,
        verbose_name="Последнее изменение",
        help_text="Дата и время последнего изменения файла"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания записи"
    )

    class Meta:
        verbose_name = "Файл лога"
        verbose_name_plural = "Файлы логов"
        ordering = ["-last_modified"]

    def __str__(self):
        return self.name

    def get_file_size_display(self):
        """Возвращает размер файла в читаемом формате"""
        size = self.size
        for unit in ['Б', 'КБ', 'МБ', 'ГБ']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} ТБ"

    def update_file_info(self):
        """Обновляет информацию о файле"""
        if os.path.exists(self.file_path):
            stat = os.stat(self.file_path)
            self.size = stat.st_size
            from django.utils import timezone
            import datetime
            self.last_modified = datetime.datetime.fromtimestamp(
                stat.st_mtime,
                tz=timezone.get_current_timezone()
            )
            self.save()


class LogBackup(models.Model):
    """
    Модель для хранения информации о резервных копиях логов.
    """
    log_file = models.ForeignKey(
        LogFile,
        on_delete=models.CASCADE,
        related_name="backups",
        verbose_name="Файл лога"
    )
    backup_file = models.FileField(
        upload_to=RenameUploadTo("logs/backups/"),
        verbose_name="Резервная копия",
        help_text="Файл резервной копии"
    )
    backup_size = models.BigIntegerField(
        default=0,
        verbose_name="Размер копии (байт)"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания копии"
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Описание",
        help_text="Дополнительное описание резервной копии"
    )

    class Meta:
        verbose_name = "Резервная копия лога"
        verbose_name_plural = "Резервные копии логов"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Копия {self.log_file.name} от {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"

    def get_backup_size_display(self):
        """Возвращает размер копии в читаемом формате"""
        size = self.backup_size
        for unit in ['Б', 'КБ', 'МБ', 'ГБ']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} ТБ"
