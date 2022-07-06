from django.db import models
from django.urls import reverse
from taggit.managers import TaggableManager
from sorl.thumbnail import get_thumbnail

def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'serials/{0}/{1}'.format(instance.slug, str(instance.slug+'.jpg'))

class Serial(models.Model):
    title = models.CharField(max_length=255, verbose_name="Название сериала")
    slug = models.SlugField(max_length=255, verbose_name="Slug", unique=True)
    rating = models.DecimalField(max_digits=5, decimal_places=3, null=True,
                                 verbose_name="Рейтинг кинопоиска")
    serialYearStart = models.IntegerField(verbose_name="Дата выхода")
    serialYearEnd = models.IntegerField(verbose_name="Дата закрытия")
    countries = models.CharField(max_length=255, verbose_name="Страна")
    serialLinkKino = models.CharField(max_length=255, verbose_name="URL в Кинопоиске", blank=True)
    posterLink = models.CharField(max_length=255, verbose_name="URL Постера", blank=True)
    published = models.BooleanField(default=True, verbose_name="Опубликовано")
    posterImage = models.ImageField(upload_to=user_directory_path, blank=True, verbose_name="Постер")
    genres = TaggableManager()

    class Meta:
        ordering = ('-rating',)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("serials:info", args=[self.slug])

    def get_genres(self):
        return ", ".join([i.name for i in self.genres.all()])



class Serial_info(models.Model):
    serial = models.OneToOneField(Serial, on_delete=models.CASCADE, primary_key=True, verbose_name="Serial_id")
    MySeriadescription = models.TextField(blank=True, verbose_name="Описание сериала")
    MySeriarating = models.DecimalField(max_digits=5, decimal_places=3, blank=True, null=True,
                                        verbose_name="Рейтинг MySeria")
    LastSerianame = models.CharField(max_length=255, blank=True, verbose_name="Последняя серия")
    LastSeriaurl = models.CharField(max_length=255, blank=True, verbose_name="URL последней серии")
    LastSeriavoice = models.CharField(max_length=255, blank=True, verbose_name="Озвучки")

    def __str__(self):
        return self.MySeriadescription[:10]
