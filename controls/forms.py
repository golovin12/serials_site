from django import forms

from taggit.models import Tag
from serials.models import Serial
import datetime


class SerialsForm(forms.ModelForm):
    class Meta:
        model = Serial
        fields = ('title', 'rating', 'serialYearStart', 'serialYearEnd', 'countries', 'serialLinkKino', 'posterLink',
                  'posterImage', 'genres', 'published')


    def clean_posterImage(self):
        cd = self.cleaned_data
        if cd['posterLink'][:4] != "http" and cd['posterLink'] != 'No_poster':
            if cd['posterLink'] == 'User_image' and cd['posterImage'] != False:
                return cd['posterLink']
            if cd['posterLink'] == 'User_image' and cd['posterImage'] == False:
                raise forms.ValidationError('Вы не добавили постер.')
            raise forms.ValidationError('Вы указали некорректную ссылку на постер.')
        return cd['posterImage']


    def clean_serialLinkKino(self):
        cd = self.cleaned_data
        if cd['serialLinkKino'][:4] != "http":
            raise forms.ValidationError('Вы ввели некорректную ссылку на сериал в кинопоиске.')
        return cd['serialLinkKino']

    def clean_rating(self):
        cd = self.cleaned_data
        if cd['rating'] > 10 or cd['rating'] < 0:
            raise forms.ValidationError('Вы указали некорректный рейтинг (рейтинг должен быть от 0 до 10).')
        return cd['rating']

    def clean_serialYearStart(self):
        cd = self.cleaned_data
        if cd['serialYearStart'] < 1900 or cd['serialYearStart'] > (int(datetime.datetime.now().year)+15):
            raise forms.ValidationError('Вы указали некорректную дату выхода сериала.')
        return cd['serialYearStart']

    def clean_serialYearEnd(self):
        cd = self.cleaned_data
        if cd['serialYearStart'] > cd['serialYearEnd'] or (cd['serialYearEnd'] > (int(datetime.datetime.now().year)+15) and cd['serialYearEnd'] != 9999):
            raise forms.ValidationError('Вы указали некорректную дату закрытия сериала.')
        return cd['serialYearEnd']

    def clean_genres(self):
        cd = self.cleaned_data
        tags = [i['name'] for i in Tag.objects.all().values('name')]
        print(tags)
        print(cd['genres'])
        for i in cd['genres']:
            if i not in tags:
                raise forms.ValidationError('Вы указали некорректный жанр сериала.')
        return cd['genres']
