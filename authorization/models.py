from django.conf import settings
from django.db import models

from serials.models import Serial


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE)
    liked_serials = models.ManyToManyField(Serial, blank=True, verbose_name='Понравившиеся сериалы')
    photo = models.ImageField(upload_to='users/', blank=True, verbose_name='Фото')
