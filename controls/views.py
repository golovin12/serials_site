import json

from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render
from pytils.translit import slugify
from taggit.models import Tag

from serials.models import Serial
from .forms import SerialsForm

def user_groups_Admin(func):
    def proverka(request):
        if request.user.groups.filter(name="Admin_for_site").exists():
            return func(request)
        else:
            raise Http404("У вас нет доступа.")

    return proverka


@login_required
@user_groups_Admin
def create_base(request):
    host = 'https://www.kinopoisk.ru/series/'
    with open('serials.json', 'r') as file:
        all_serials = json.load(file)
        point = 0
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
                    one_serial = Serial(title=title, slug=slugify(title), rating=rating,
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
                    one_serial.save()
                    for i in genres:
                        one_serial.genres.add(i)
                    point += 1
                except Exception as ex:
                    one_serial = Serial(title=(title), slug=(slugify(title) + "-" + str(index1 * 50 + index2)),
                                        rating=rating,
                                        serialYearStart=int(serialYearStart),
                                        serialYearEnd=int(serialYearEnd), countries=countries,
                                        serialLinkKino=serialLink,
                                        posterLink=posterLink)
                    one_serial.save()
                    for i in genres:
                        one_serial.genres.add(i)
                    point += 1
    return render(request, "controls/result.html", {'point': point, "type": "create_serials"})


@login_required
@user_groups_Admin
def update_serials(request):
    pass


@login_required
@user_groups_Admin
def update_all(request):
    pass


@login_required
@user_groups_Admin
def update_last(request):
    pass


@login_required
@user_groups_Admin
def add_serials(request):
    if request.method == 'GET':
        serials_form = SerialsForm()
    elif request.method == 'POST':
        serials_form = SerialsForm(data=request.POST, files=request.FILES)
        if serials_form.is_valid():
            print('Da')
            # serials_form.save()
    else:
        serials_form = SerialsForm()
    return render(request, 'base.html', {'form': serials_form.as_p()})
    # title = request.POST.get('title')
        # rating = request.POST.get('rating')
        # serialYearStart = request.POST.get('serialYearStart')
        # serialYearEnd = request.POST.get('serialYearEnd')
        # countries = request.POST.get('countries')
        # serialLink = request.POST.get('serialLink')
        # posterLink = request.POST.get('posterLink')
        # posterImage = request.POST.get('posterImage')
        # genres = request.POST.get('genres')
        # one_serial = Serial(title=(title), slug=(slugify(title) + "-"),
        #                     rating=rating,
        #                     serialYearStart=int(serialYearStart),
        #                     serialYearEnd=int(serialYearEnd), countries=countries,
        #                     serialLinkKino=serialLink,
        #                     posterLink=posterLink)
        # one_serial.save()


@login_required
@user_groups_Admin
def delete_serials(request):
    pass


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
