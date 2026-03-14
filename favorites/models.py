from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _
from accounts.models import User


class Favorite(models.Model):
    """
    Система избранного — пользователь может "лайкнуть" любой объект на сайте
    (новость, портфолио, услугу) с помощью Generic Foreign Key.

    Использование:
        Favorite.objects.toggle(user, obj)  → добавить/удалить
        Favorite.objects.is_favorite(user, obj) → проверить
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name=_('Пользователь')
    )
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        verbose_name=_('Тип объекта')
    )
    object_id = models.PositiveIntegerField(verbose_name=_('ID объекта'))
    content_object = GenericForeignKey('content_type', 'object_id')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Добавлено'))

    class Meta:
        verbose_name = _('Избранное')
        verbose_name_plural = _('Избранное')
        unique_together = ('user', 'content_type', 'object_id')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user} → {self.content_type.model} #{self.object_id}'
