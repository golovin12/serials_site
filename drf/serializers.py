from django.utils import timezone
from pytils.translit import slugify
from rest_framework import serializers
from sorl_thumbnail_serializer.fields import HyperlinkedSorlImageField
from taggit.models import Tag
from taggit.serializers import TagListSerializerField, TaggitSerializer

from serials.models import Serial, Serial_info


# class SerialInfoSerializer(serializers.Serializer):
#     MySeriadescription = serializers.CharField(trim_whitespace=True)
#     MySeriarating = serializers.DecimalField(max_digits=5, decimal_places=3)
#     LastSerianame = serializers.CharField(max_length=255, trim_whitespace=True)
#     LastSeriaurl = serializers.CharField(max_length=255, trim_whitespace=True)
#     LastSeriavoice = serializers.CharField(max_length=255, trim_whitespace=True)


# class SerialSerializer(serializers.Serializer):
#     title = serializers.CharField(max_length=255, trim_whitespace=True)
#     slug = serializers.SlugField(max_length=255, read_only=True)
#     rating = serializers.DecimalField(max_digits=5, decimal_places=3)
#     serialYearStart = serializers.IntegerField()
#     serialYearEnd = serializers.IntegerField()
#     countries = serializers.CharField(max_length=255, trim_whitespace=True)
#     serialLinkKino = serializers.CharField(max_length=255, write_only=True, trim_whitespace=True)
#     posterLink = serializers.CharField(max_length=255, write_only=True, trim_whitespace=True)
#     published = serializers.BooleanField(write_only=True)
#     posterImage = serializers.ImageField(use_url=True)
#     genres = GenresSerializer(many=True)


class SerialInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Serial_info
        fields = ['MySeriadescription', 'MySeriarating', 'LastSerianame', 'LastSeriaurl', 'LastSeriavoice']


class SerialsSerializer(TaggitSerializer, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Serial
        fields = ['title', 'slug', 'rating', 'serialYearStart', 'serialYearEnd', 'countries', 'serialLinkKino',
                  'posterImage', 'genres', 'thumbnail']
        read_only_fields = ['__all__']

    genres = TagListSerializerField()
    thumbnail = HyperlinkedSorlImageField(
        'x100',
        options={"crop": "center"},
        source='posterImage',
        read_only=True
    )
    # A larger version of the image, allows writing
    posterImage = HyperlinkedSorlImageField('1024')


class SerialSerializer(TaggitSerializer, serializers.ModelSerializer):
    serial_info = SerialInfoSerializer(read_only=True)
    genres = TagListSerializerField()

    class Meta:
        model = Serial
        fields = ['title', 'slug', 'rating', 'serialYearStart', 'serialYearEnd', 'countries', 'serialLinkKino',
                  'posterLink', 'posterImage', 'genres', 'published', 'serial_info', 'thumbnail']
        extra_kwargs = {'published': {'write_only': True}, 'posterLink': {'trim_whitespace': True, 'write_only': True},
                        'serialLinkKino': {'trim_whitespace': True}, 'countries': {'trim_whitespace': True},
                        'rating': {'max_digits': 5, 'decimal_places': 3}, 'title': {'trim_whitespace': True},
                        'slug': {'read_only': True}}

    thumbnail = HyperlinkedSorlImageField(
        'x400',
        options={"crop": "center"},
        source='posterImage',
        read_only=True
    )
    posterImage = HyperlinkedSorlImageField('1024', allow_null=True)

    def create(self, validated_data):
        print(validated_data)
        slug = create_slug(slugify(validated_data["title"]))
        genres = validated_data.pop('genres')
        serial = Serial(slug=slug, **validated_data)
        serial.save()
        for genr in genres:
            serial.genres.add(genr)
        return serial

    def validate(self, data):
        if data['serialLinkKino'][:4] != "http":
            raise serializers.ValidationError('Вы ввели некорректную ссылку на сериал в кинопоиске.')
        if data['rating'] > 10 or data['rating'] < 0:
            raise serializers.ValidationError('Вы указали некорректный рейтинг (рейтинг должен быть от 0 до 10).')
        if data['serialYearStart'] < 1900 or data['serialYearStart'] > (int(timezone.datetime.now().year) + 15):
            raise serializers.ValidationError('Вы указали некорректную дату выхода сериала.')
        if data['serialYearStart'] > data['serialYearEnd'] or (
                data['serialYearEnd'] > (int(timezone.now().year) + 15) and data['serialYearEnd'] != 9999):
            raise serializers.ValidationError('Вы указали некорректную дату закрытия сериала.')
        tags = [i['name'] for i in Tag.objects.all().values('name')]
        print(data['genres'])
        print(tags)
        if len(data['genres']) == 0:
            raise serializers.ValidationError('Жанр сериала обязателен к заполнению.')
        else:
            for i in data['genres']:
                if i not in tags:
                    raise serializers.ValidationError('Вы указали некорректный жанр сериала.')
        return data


def create_slug(slug):
    if Serial.objects.filter(slug=slug).exists():
        slug += "-"
        sl = 1
        while Serial.objects.filter(slug=(slug + str(sl))).exists():
            sl += 1
        slug += str(sl)
    return slug
