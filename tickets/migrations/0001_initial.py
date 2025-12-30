# Generated manually

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Ticket',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(max_length=200, verbose_name='Тема')),
                ('description', models.TextField(verbose_name='Описание')),
                ('status', models.CharField(choices=[('open', 'Открыт'), ('in_progress', 'В работе'), ('resolved', 'Решен'), ('closed', 'Закрыт')], default='open', max_length=20, verbose_name='Статус')),
                ('priority', models.CharField(choices=[('low', 'Низкий'), ('medium', 'Средний'), ('high', 'Высокий'), ('urgent', 'Срочный')], default='medium', max_length=20, verbose_name='Приоритет')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Создан')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Обновлен')),
                ('closed_at', models.DateTimeField(blank=True, null=True, verbose_name='Закрыт')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tickets', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Тикет',
                'verbose_name_plural': 'Тикеты',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='TicketMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField(verbose_name='Сообщение')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Создано')),
                ('is_internal', models.BooleanField(default=False, verbose_name='Внутреннее сообщение')),
                ('ticket', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='tickets.ticket', verbose_name='Тикет')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Автор')),
            ],
            options={
                'verbose_name': 'Сообщение тикета',
                'verbose_name_plural': 'Сообщения тикетов',
                'ordering': ['created_at'],
            },
        ),
    ]

