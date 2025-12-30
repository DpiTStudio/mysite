from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """Расширенная модель пользователя"""
    phone = models.CharField(max_length=20, blank=True, verbose_name="Телефон")
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True, verbose_name="Аватар")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата регистрации")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    
    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ["-created_at"]
    
    def __str__(self):
        return self.username
