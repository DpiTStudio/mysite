import logging
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_service_order_notifications_task(self, order_id: int) -> None:
    """
    Фоновая задача Celery для отправки email-уведомлений администратору и клиенту.
    """
    from .models import ServiceOrder
    try:
        instance = ServiceOrder.objects.select_related('service', 'user').get(pk=order_id)
    except ServiceOrder.DoesNotExist:
        logger.error(f"ServiceOrder ID={order_id} не найден для отправки уведомлений.")
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
        try:
            send_mail(
                subject=admin_subject,
                message=admin_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[admin_email],
                fail_silently=False,
            )
        except Exception as exc:
            logger.error(f"Ошибка при отправке email администратору (заказ {order_id}): {exc}")

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
        try:
            send_mail(
                subject=client_subject,
                message=client_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[instance.email],
                fail_silently=False,
            )
        except Exception as exc:
            logger.error(f"Ошибка при отправке email клиенту (заказ {order_id}): {exc}")
