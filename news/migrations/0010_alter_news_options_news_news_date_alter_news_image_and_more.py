# Generated manually for data migration

from django.db import migrations, models
from django.utils import timezone
import main.utils


def migrate_existing_news(apps, schema_editor):
    """
    Миграция существующих новостей:
    1. Устанавливаем news_date из created_at
    2. Если есть дубликаты по (category, news_date), добавляем суффикс к дате
    """
    News = apps.get_model('news', 'News')
    
    # Получаем все новости
    all_news = News.objects.all().order_by('created_at')
    
    # Словарь для отслеживания использованных комбинаций (category_id, date)
    used_combinations = set()
    
    for news in all_news:
        # Устанавливаем news_date из created_at
        base_date = news.created_at.date()
        news_date = base_date
        
        # Проверяем уникальность комбинации (category, date)
        combination = (news.category_id, news_date)
        
        # Если комбинация уже используется, сдвигаем дату на 1 день
        days_offset = 0
        while combination in used_combinations:
            days_offset += 1
            from datetime import timedelta
            news_date = base_date + timedelta(days=days_offset)
            combination = (news.category_id, news_date)
        
        # Сохраняем комбинацию как использованную
        used_combinations.add(combination)
        
        # Обновляем news_date
        news.news_date = news_date
        news.save(update_fields=['news_date'])


def reverse_migration(apps, schema_editor):
    """Откат миграции - ничего не делаем"""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0009_alter_comment_options_comment_updated_at_and_more'),
    ]

    operations = [
        # Сначала добавляем поле news_date без unique constraint
        migrations.AddField(
            model_name='news',
            name='news_date',
            field=models.DateField(
                default=timezone.now,
                help_text='Дата, к которой относятся события (год, месяц, день)',
                verbose_name='Дата новости'
            ),
        ),
        # Делаем image необязательным
        migrations.AlterField(
            model_name='news',
            name='image',
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to=main.utils.RenameUploadTo('news/images/'),
                verbose_name='Изображение'
            ),
        ),
        # Мигрируем данные
        migrations.RunPython(migrate_existing_news, reverse_migration),
        # Теперь добавляем unique constraint
        migrations.AlterUniqueTogether(
            name='news',
            unique_together={('category', 'news_date')},
        ),
        # Обновляем ordering
        migrations.AlterModelOptions(
            name='news',
            options={
                'ordering': ['-news_date', '-created_at'],
                'verbose_name': 'Новость',
                'verbose_name_plural': 'Новости'
            },
        ),
    ]

