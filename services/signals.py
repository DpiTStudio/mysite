# signals.py
"""
Модуль сигналов приложения services.
Отвечает за автоматическую отправку уведомлений при создании заказов.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import ServiceOrder

@receiver(post_save, sender=ServiceOrder)
def send_order_notification(sender, instance, created, **kwargs):
    """
    Сигнал, срабатывающий после сохранения заказа услуги.
    Если заказ только что создан (created=True), отправляет email-уведомления:
    1. Администратору сайта о новом заказе.
    2. Клиенту как подтверждение получения заказа.
    """
    if created:
        site_name = getattr(settings, 'SITE_NAME', 'DPIT CMS')
        admin_email = getattr(settings, 'ADMIN_EMAIL', None)
        
        if admin_email:
            # Отправка email администратору
            subject = f'Новый заказ услуги: {instance.service.title}'
            message = f'''
            Новый заказ услуги:
            
            Услуга: {instance.service.title}
            Заказчик: {instance.full_name}
            Телефон: {instance.phone}
            Email: {instance.email}
            Сообщение: {instance.message}
            Номер заказа: {instance.short_id}
            
            ---
            {site_name}
            '''
            
            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [admin_email],
                    fail_silently=True,
                )
            except Exception:
                pass
        
        # Отправка подтверждения клиенту
        if instance.email:
            client_subject = f'Подтверждение заказа услуги: {instance.service.title}'
            client_message = f'''
            Уважаемый(ая) {instance.full_name},
            
            Спасибо за ваш заказ!
            
            Детали заказа:
            Услуга: {instance.service.title}
            Номер заказа: {instance.short_id}
            Статус: {instance.get_status_display()}
            
            Мы свяжемся с вами в ближайшее время.
            
            С уважением,
            Команда {site_name}
            '''
            
            try:
                send_mail(
                    client_subject,
                    client_message,
                    settings.DEFAULT_FROM_EMAIL,
                    [instance.email],
                    fail_silently=True,
                )
            except Exception:
                pass
