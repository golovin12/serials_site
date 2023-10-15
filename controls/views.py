import json
import random

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, UpdateView, CreateView, DeleteView
from pytils.translit import slugify
from taggit.models import Tag

from serials.filters_serials import filters_serials
from serials.models import Serial
from .forms import SerialsForm


# Декоратор, отвечающий за проверку принадлежности юзера к группе админа.
def user_groups_Admin(func):
    def proverka(request):
        if request.user.is_superuser or request.user.groups.filter(name="Admin_for_site").exists():
            return func(request)
        else:
            raise Http404("У вас нет доступа.")

    return proverka


def clean_posterLink(info):
    cd = info
    if cd['posterLink'][:4] != "http" and cd['posterLink'] != 'No_poster':
        if cd['posterLink'] == 'User_image' and cd['posterImage'] != None:
            return cd['posterLink']
        if cd['posterLink'] == 'User_image' and cd['posterImage'] == None:
            return False
        return False
    return cd['posterLink']


class ListSerials(UserPassesTestMixin, ListView):
    # template_name = 'controls/add.html'
    template_name = 'serials/categories.html'

    def test_func(self):
        return self.request.user.groups.filter(name="Admin_for_site").exists()

    def get_queryset(self):
        self.published = Serial.objects.all()
        return self.published

    def get_context_data(self, **kwargs):
        link = 'controls:all'
        name = 'categories'
        context = filters_serials(self.request, self.published, link, name)[1]
        return context


class EditSerial(UserPassesTestMixin, UpdateView):
    model = Serial
    form_class = SerialsForm
    template_name = 'controls/edit.html'

    def test_func(self):
        return self.request.user.groups.filter(name="Admin_for_site").exists()

    def get_context_data(self, **kwargs):
        serial_slug = self.object.slug
        return super().get_context_data(serial_slug=serial_slug, **kwargs)

    def get_success_url(self):
        return reverse("serials:info", kwargs={"slug": self.kwargs['slug']})

    def form_valid(self, form):
        if self.request.FILES.get('posterImage-clear') is not None and (
                self.request.POST['posterLink'] != 'No_poster' or self.request.POST['posterLink'][:4] != "http"):
            form.add_error('posterLink', 'Вы не можете оставить картинку пустой, не указав: "No_poster"')
            return self.render_to_response(self.get_context_data(form=form))
        if self.request.POST['posterLink'][:4] != "http" and self.request.POST['posterLink'] not in ["User_image",
                                                                                                     "No_poster"]:
            form.add_error('posterLink', 'Вы указали некорректную ссылку')
            return self.render_to_response(self.get_context_data(form=form))
        self.object = form.save()
        return HttpResponseRedirect(self.get_success_url())


class AddSerial(UserPassesTestMixin, CreateView):
    model = Serial
    form_class = SerialsForm
    template_name = 'controls/add.html'

    def test_func(self):
        return self.request.user.groups.filter(name="Admin_for_site").exists()

    def get_success_url(self):
        return reverse("serials:info", kwargs={"slug": self.object.slug})

    def post(self, request, *args, **kwargs):
        slug = create_slug(slugify(self.request.POST["title"]))
        self.object = Serial(slug=slug)
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        result = clean_posterLink(
            {'posterImage': self.request.FILES.get('posterImage'), 'posterLink': self.request.POST['posterLink']})
        if result == False:
            form.add_error('posterLink', 'Вы указали некорректную ссылку')
            return self.render_to_response(self.get_context_data(form=form))
        return super().form_valid(form)


class DeleteSerial(UserPassesTestMixin, DeleteView):
    model = Serial
    template_name = 'controls/delete.html'
    success_url = reverse_lazy('controls:all')

    def get_context_data(self, **kwargs):
        serial_name = self.object.title
        return super().get_context_data(serial_name=serial_name, **kwargs)

    def test_func(self):
        return self.request.user.groups.filter(name="Admin_for_site").exists()


def create_slug(slug):
    if Serial.objects.filter(slug=slug).exists():
        slug += "-"
        sl = 1
        while Serial.objects.filter(slug=(slug + str(sl))).exists():
            sl += 1
        slug += str(sl)
    return slug


@login_required
@user_groups_Admin
def create_base(request):
    host = 'https://www.kinopoisk.ru/series/'
    with open('serials.json', 'r') as file:
        all_serials = json.load(file)
        point = 0

        use_nicks = set()

        save = []
        genres_for_save = []

        for index1, i in enumerate(all_serials):
            page_serials = all_serials.get(i).get('itemsInfo')
            for index2, serial in enumerate(page_serials, start=1):
                try:
                    coreData = serial.get('coreData')
                    serialLink = host + str(coreData.get('id')) + "/"
                    posterLink = coreData.get('posterLink')
                    title = coreData.get('title')
                    serialYearStart = coreData.get('serialYears').get('start')
                    serialYearEnd = coreData.get('serialYears').get('end')
                    if serialYearStart is None:
                        serialYearStart = coreData.get('year')
                        serialYearEnd = coreData.get('year')
                    if serialYearEnd is None:
                        serialYearEnd = 9999
                    if title == "":
                        title = coreData.get('originalTitle')
                    if posterLink[:4] != "http":
                        posterLink = "No_poster"
                    rating = float(coreData.get('ratings').get('rating').get('value'))
                    countries = ", ".join(i.get('name') for i in coreData.get('countries'))
                    genres = [i.get('name') for i in coreData.get('genres')]

                    if coreData.get('id') == 951953:
                        countries = "Россия"
                        genres = ["боевик", "детектив"]
                    if coreData.get('id') == 1402881:
                        countries = "Россия"
                        genres = ["детектив", "триллер"]
                    if coreData.get('id') == 1119454 or coreData.get('id') == 1007525:
                        countries = "Великобритания"
                    if coreData.get('id') == 840893 or coreData.get('id') == 927628 or coreData.get('id') == 1368895:
                        countries = "США"
                    if coreData.get('id') == 838243:
                        countries = "Япония"
                    if coreData.get('id') == 1244945:
                        countries = "Турция"
                    if coreData.get('id') in [829742, 1138772, 1254053, 471702, 935910, 425846, 477458, 422804]:
                        genres = ["мелодрама"]
                    if coreData.get('id') in [843039, 468308]:
                        genres = ["детектив"]
                    if coreData.get('id') in [1048954, 969834]:
                        genres = ["детектив", "мелодрама"]
                    if coreData.get('id') == 932498:
                        genres = ["детектив", "драма"]
                    if coreData.get('id') in [697444, 585283, 708362]:
                        continue
                    if coreData.get('id') == 932498:
                        genres = ["детектив", "драма"]
                    if coreData.get('id') == 464899:
                        genres = ["триллер"]
                    if coreData.get('id') == 478823:
                        genres = ["драма", "криминал"]
                    if coreData.get('id') in [910028, 471024]:
                        genres = ["документальный"]
                    if coreData.get('id') in [679595, 766829, 581867]:
                        genres = ["драма"]
                    if coreData.get('id') == 628880:
                        genres = ["боевик"]
                    if coreData.get('id') in [453107]:
                        genres = ["драма", "мелодрама"]
                    if coreData.get('id') in [160952]:
                        genres = ["боевик", "детектив"]
                    if coreData.get('id') == 402951:
                        genres = ["реальное ТВ"]
                    slug = slugify(title[:])
                    while slug in use_nicks:
                        slug += str(random.randint(1000000, 10000000))
                    use_nicks.add(slug)
                    one_serial = Serial(title=title, slug=slug, rating=rating,
                                        serialYearStart=int(serialYearStart),
                                        serialYearEnd=int(serialYearEnd), countries=countries,
                                        serialLinkKino=serialLink,
                                        posterLink=posterLink)
                    # print(f"Сериал {index1 * 50 + index2}: {title}\n"
                    #       f"Ссылка: {serialLink}\n"
                    #       f"Рейтинг: {rating}\n"
                    #       f"Годы существования: {serialYearStart}-{serialYearEnd}\n"
                    #       f"Страны: {countries}\n"
                    #       f"Жанр: {genres}\n"
                    #       f"Ссылка на картинку: {posterLink}\n\n")
                    save.append(one_serial)
                    genres_for_save.append(genres)
                    if len(save) % 500 == 0:
                        if point > 1000:
                            Serial.objects.bulk_create(save)
                            for index, gfs in enumerate(genres_for_save):
                                for gen in gfs:
                                    save[index].genres.add(gen)
                        save = []
                        genres_for_save = []
                    # one_serial.save()
                    # for i in genres:
                    #     one_serial.genres.add(i)
                    point += 1
                except Exception as ex:
                    pass
                    # one_serial = Serial(title=(title), slug=(slugify(title) + "-" + str(index1 * 50 + index2)),
                    #                     rating=rating,
                    #                     serialYearStart=int(serialYearStart),
                    #                     serialYearEnd=int(serialYearEnd), countries=countries,
                    #                     serialLinkKino=serialLink,
                    #                     posterLink=posterLink)
                    #
                    # save.append(one_serial)
                    # genres_for_save.append(genres)
                    #
                    # if len(save) % 500 == 0:
                    #     Serial.objects.bulk_create(save)
                    #     for index, gfs in enumerate(genres_for_save):
                    #         for gen in gfs:
                    #             save[index].genres.add(gen)
                    #     save = []
                    #     genres_for_save = []
                    # one_serial.save()
                    # for i in genres:
                    #     one_serial.genres.add(i)
                    point += 1
        if len(save) != 0:
            Serial.objects.bulk_create(save)
            for index, gfs in enumerate(genres_for_save):
                for gen in gfs:
                    save[index].genres.add(gen)
    return render(request, "controls/result.html", {'point': point, "type": "create_serials"})


@login_required
@user_groups_Admin
def tags_slug_update(request):
    point = 0
    tags = Tag.objects.all()
    for tag in tags:
        tag.slug = slugify(tag.name)
        tag.save()
        point += 1
    return render(request, "controls/result.html", {'point': point, "type": "tags"})
