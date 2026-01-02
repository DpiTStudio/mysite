from django.db import models
from django.contrib.auth.models import AbstractUser
from main.utils import RenameUploadTo
from main.models import TimestampModel


class User(AbstractUser, TimestampModel):
    """Расширенная модель пользователя"""
    phone = models.CharField(max_length=20, blank=True, verbose_name="Телефон")
    avatar = models.ImageField(upload_to=RenameUploadTo("avatars/"), blank=True, null=True, verbose_name="Аватар")
    
    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ["-created_at"]
    
    def __str__(self):
        return self.username
