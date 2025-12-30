from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from .models import LogFile, LogBackup
import os
import shutil
from pathlib import Path
from django.conf import settings
from django.utils import timezone
import datetime


@admin.register(LogFile)
class LogFileAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "file_path_display",
        "size_display",
        "last_modified",
        "backups_count",
        "actions_column"
    ]
    list_filter = ["last_modified", "created_at"]
    search_fields = ["name", "file_path"]
    readonly_fields = [
        "name",
        "file_path",
        "size",
        "last_modified",
        "created_at",
        "file_content_preview"
    ]

    def changelist_view(self, request, extra_context=None):
        """Автоматически синхронизируем логи при открытии списка"""
        try:
            log_dir = Path(settings.BASE_DIR) / "logs"
            if log_dir.exists():
                log_files = list(log_dir.glob('*.log'))
                for log_file_path in log_files:
                    file_name = log_file_path.name
                    file_path = str(log_file_path.absolute())
                    log_file, created = LogFile.objects.get_or_create(
                        file_path=file_path,
                        defaults={'name': file_name}
                    )
                    if not created:
                        log_file.update_file_info()
        except Exception:
            pass  # Игнорируем ошибки синхронизации
        return super().changelist_view(request, extra_context)

    fieldsets = (
        (
            "Информация о файле",
            {
                "fields": (
                    "name",
                    "file_path",
                    "size",
                    "last_modified",
                    "created_at"
                )
            }
        ),
        (
            "Содержимое файла",
            {
                "fields": ("file_content_preview",),
                "classes": ("collapse",)
            }
        ),
    )

    def file_path_display(self, obj):
        """Отображает путь к файлу"""
        return format_html(
            '<span style="font-family: monospace; font-size: 0.9em;">{}</span>',
            obj.file_path
        )
    file_path_display.short_description = "Путь к файлу"

    def size_display(self, obj):
        """Отображает размер файла"""
        return obj.get_file_size_display()
    size_display.short_description = "Размер"

    def backups_count(self, obj):
        """Показывает количество резервных копий"""
        count = obj.backups.count()
        if count > 0:
            url = reverse("admin:logfiles_logbackup_changelist")
            return format_html(
                '<a href="{}?log_file__id__exact={}">{} копий</a>',
                url,
                obj.id,
                count
            )
        return "Нет копий"
    backups_count.short_description = "Резервные копии"

    def actions_column(self, obj):
        """Колонка с действиями"""
        return format_html(
            '<a class="button" href="{}" style="margin-right: 5px;">Создать копию</a>'
            '<a class="button" href="{}" style="margin-right: 5px;">Очистить</a>'
            '<a class="button" href="{}">Обновить</a>',
            reverse("admin:logfiles_logfile_create_backup", args=[obj.pk]),
            reverse("admin:logfiles_logfile_clear_log", args=[obj.pk]),
            reverse("admin:logfiles_logfile_refresh", args=[obj.pk])
        )
    actions_column.short_description = "Действия"

    def file_content_preview(self, obj):
        """Показывает последние строки файла"""
        if not os.path.exists(obj.file_path):
            return "Файл не найден"
        
        try:
            with open(obj.file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                # Показываем последние 50 строк
                preview_lines = lines[-50:] if len(lines) > 50 else lines
                content = ''.join(preview_lines)
                
                return format_html(
                    '<pre style="max-height: 400px; overflow-y: auto; '
                    'background: #f5f5f5; padding: 10px; border: 1px solid #ddd; '
                    'font-family: monospace; font-size: 12px;">{}</pre>',
                    content
                )
        except Exception as e:
            return f"Ошибка чтения файла: {str(e)}"
    file_content_preview.short_description = "Предпросмотр (последние 50 строк)"

    def get_urls(self):
        """Добавляет кастомные URL для действий"""
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:logfile_id>/create_backup/',
                self.admin_site.admin_view(self.create_backup),
                name='logfiles_logfile_create_backup',
            ),
            path(
                '<int:logfile_id>/clear_log/',
                self.admin_site.admin_view(self.clear_log),
                name='logfiles_logfile_clear_log',
            ),
            path(
                '<int:logfile_id>/refresh/',
                self.admin_site.admin_view(self.refresh_log),
                name='logfiles_logfile_refresh',
            ),
        ]
        return custom_urls + urls

    def create_backup(self, request, logfile_id):
        """Создает резервную копию лога"""
        try:
            log_file = LogFile.objects.get(pk=logfile_id)
            
            if not os.path.exists(log_file.file_path):
                messages.error(request, f"Файл {log_file.file_path} не найден!")
                return redirect("admin:logfiles_logfile_changelist")
            
            # Создаем директорию для резервных копий, если её нет
            backup_dir = Path(settings.MEDIA_ROOT) / "logs" / "backups"
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Генерируем имя файла с временной меткой
            timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"{log_file.name}_{timestamp}.log"
            backup_path = backup_dir / backup_filename
            
            # Копируем файл
            shutil.copy2(log_file.file_path, backup_path)
            
            # Создаем запись в БД
            backup = LogBackup.objects.create(
                log_file=log_file,
                backup_file=f"logs/backups/{backup_filename}",
                backup_size=os.path.getsize(backup_path),
                description=f"Автоматическая резервная копия от {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            
            messages.success(
                request,
                f"Резервная копия успешно создана: {backup_filename} "
                f"({backup.get_backup_size_display()})"
            )
        except LogFile.DoesNotExist:
            messages.error(request, "Файл лога не найден!")
        except Exception as e:
            messages.error(request, f"Ошибка при создании резервной копии: {str(e)}")
        
        return redirect("admin:logfiles_logfile_changelist")

    def clear_log(self, request, logfile_id):
        """Очищает содержимое лог-файла"""
        if request.method == 'POST':
            try:
                log_file = LogFile.objects.get(pk=logfile_id)
                
                if not os.path.exists(log_file.file_path):
                    messages.error(request, f"Файл {log_file.file_path} не найден!")
                    return redirect("admin:logfiles_logfile_changelist")
                
                # Создаем резервную копию перед очисткой
                backup_dir = Path(settings.MEDIA_ROOT) / "logs" / "backups"
                backup_dir.mkdir(parents=True, exist_ok=True)
                timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
                backup_filename = f"{log_file.name}_before_clear_{timestamp}.log"
                backup_path = backup_dir / backup_filename
                shutil.copy2(log_file.file_path, backup_path)
                
                # Очищаем файл
                with open(log_file.file_path, 'w', encoding='utf-8') as f:
                    f.write('')
                
                # Обновляем информацию о файле
                log_file.update_file_info()
                
                # Создаем запись о резервной копии
                LogBackup.objects.create(
                    log_file=log_file,
                    backup_file=f"logs/backups/{backup_filename}",
                    backup_size=os.path.getsize(backup_path),
                    description=f"Автоматическая копия перед очисткой от {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}"
                )
                
                messages.success(
                    request,
                    f"Лог-файл очищен. Создана резервная копия: {backup_filename}"
                )
            except LogFile.DoesNotExist:
                messages.error(request, "Файл лога не найден!")
            except Exception as e:
                messages.error(request, f"Ошибка при очистке файла: {str(e)}")
            
            return redirect("admin:logfiles_logfile_changelist")
        else:
            # Показываем страницу подтверждения
            from django.template.response import TemplateResponse
            log_file = LogFile.objects.get(pk=logfile_id)
            context = {
                **self.admin_site.each_context(request),
                'title': 'Подтверждение очистки лога',
                'log_file': log_file,
                'opts': self.model._meta,
                'has_view_permission': self.has_view_permission(request, log_file),
            }
            return TemplateResponse(
                request,
                'admin/logfiles/logfile/confirm_clear.html',
                context
            )

    def refresh_log(self, request, logfile_id):
        """Обновляет информацию о файле лога"""
        try:
            log_file = LogFile.objects.get(pk=logfile_id)
            log_file.update_file_info()
            messages.success(request, "Информация о файле обновлена!")
        except LogFile.DoesNotExist:
            messages.error(request, "Файл лога не найден!")
        except Exception as e:
            messages.error(request, f"Ошибка при обновлении: {str(e)}")
        
        return redirect("admin:logfiles_logfile_changelist")

    def has_add_permission(self, request):
        """Запрещаем ручное добавление файлов логов"""
        return False

    def has_delete_permission(self, request, obj=None):
        """Запрещаем удаление файлов логов через админку"""
        return False


@admin.register(LogBackup)
class LogBackupAdmin(admin.ModelAdmin):
    list_display = [
        "log_file",
        "backup_file",
        "backup_size_display",
        "created_at",
        "download_link"
    ]
    list_filter = ["created_at", "log_file"]
    search_fields = ["log_file__name", "description"]
    readonly_fields = [
        "log_file",
        "backup_file",
        "backup_size",
        "created_at",
        "download_link"
    ]
    date_hierarchy = "created_at"

    fieldsets = (
        (
            "Информация о резервной копии",
            {
                "fields": (
                    "log_file",
                    "backup_file",
                    "backup_size",
                    "created_at",
                    "description"
                )
            }
        ),
        (
            "Действия",
            {
                "fields": ("download_link",)
            }
        ),
    )

    def backup_size_display(self, obj):
        """Отображает размер копии"""
        return obj.get_backup_size_display()
    backup_size_display.short_description = "Размер"

    def download_link(self, obj):
        """Ссылка для скачивания резервной копии"""
        if obj.backup_file:
            url = obj.backup_file.url
            return format_html(
                '<a href="{}" target="_blank" class="button">Скачать копию</a>',
                url
            )
        return "Файл не найден"
    download_link.short_description = "Скачать"

    def has_add_permission(self, request):
        """Запрещаем ручное добавление резервных копий"""
        return False
