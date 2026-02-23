import threading
import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import ServiceOrder

logger = logging.getLogger(__name__)

def send_notification_email_async(subject: str, message: str, recipient_list: list) -> None:
    """
    Асинхронная отправка email в отдельном потоке.
    Предотвращает блокировку основного потока выполнения при создании заказа.
    """
    def send():
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipient_list,
                fail_silently=True,
            )
        except Exception as e:
            logger.error(f"Ошибка при отправке email ({subject}): {e}")
            
    thread = threading.Thread(target=send)
    thread.start()

@receiver(post_save, sender=ServiceOrder)
def send_order_notification(sender, instance, created, **kwargs):
    """
    Сигнал, срабатывающий после сохранения заказа услуги.
    Отправляет уведомления в асинхронном режиме:
    1. Администратору сайта (о новом заказе).
    2. Клиенту (как подтверждение получения заказа).
    """
    if not created:
        return

    site_name = getattr(settings, 'SITE_NAME', 'DPIT CMS')
    admin_email = getattr(settings, 'ADMIN_EMAIL', None)
    
    # 1. Отправка уведомления администратору
    if admin_email:
        admin_subject = f'Новый заказ услуги: {instance.service.title}'
        admin_message = (
            f"Поступил новый заказ услуги на сайте {site_name}:\n\n"
            f"Услуга: {instance.service.title}\n"
            f"Заказчик: {instance.full_name}\n"
            f"Телефон: {instance.phone}\n"
            f"Email: {instance.email or 'Не указан'}\n"
            f"Сообщение:\n{instance.message or 'Без сообщения'}\n\n"
            f"Номер заказа: {instance.short_id}\n\n"
            f"---\nАвтоматическое уведомление {site_name}"
        )
        send_notification_email_async(admin_subject, admin_message, [admin_email])
    
    # 2. Отправка подтверждения клиенту
    if instance.email:
        client_subject = f'Подтверждение заказа: {instance.service.title}'
        client_message = (
            f"Уважаемый(ая) {instance.full_name},\n\n"
            f"Благодарим вас за заказ на сайте {site_name}!\n\n"
            f"Детали вашего заказа:\n"
            f"• Услуга: {instance.service.title}\n"
            f"• Номер заказа: {instance.short_id}\n"
            f"• Текущий статус: {instance.get_status_display()}\n\n"
            f"Наш менеджер свяжется с вами в ближайшее время для уточнения деталей.\n\n"
            f"С уважением,\nКоманда {site_name}"
        )
        send_notification_email_async(client_subject, client_message, [instance.email])
