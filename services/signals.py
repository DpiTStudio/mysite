import threading
import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ServiceOrder
from .tasks import send_service_order_notifications_task

logger = logging.getLogger(__name__)

@receiver(post_save, sender=ServiceOrder)
def send_order_notification(sender, instance, created, **kwargs):
    """
    Сигнал, срабатывающий после сохранения заказа услуги.
    Запускает отправку уведомлений в фоновой задаче Celery с безопасным фолбэком на поток.
    """
    if not created:
        return

    try:
        # Пытаемся отправлять через Celery
        send_service_order_notifications_task.delay(instance.pk)
    except Exception as exc:
        logger.warning(f"Не удалось отправить задачу в Celery ({exc}), запуск в отдельном потоке...")
        def fallback_run():
            try:
                send_service_order_notifications_task(instance.pk)
            except Exception as e:
                logger.error(f"Ошибка при фолбэк-отправке уведомления: {e}")
        thread = threading.Thread(target=fallback_run)
        thread.start()
