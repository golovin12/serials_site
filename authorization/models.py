from django.conf import settings
from django.db import models

from serials.models import Serial

def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'users/{0}/{1}'.format(instance.user.username, filename)

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE)
    liked_serials = models.ManyToManyField(Serial, blank=True, verbose_name='Понравившиеся сериалы')
    photo = models.ImageField(upload_to=user_directory_path, blank=True, verbose_name='Фото')
