import io

import redis
import requests
from bs4 import BeautifulSoup
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Count
from django.http import HttpResponseNotFound
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse

from authorization.models import Profile
from .filters_serials import filters_serials
from .models import Serial, Serial_info

redis_instance = redis.StrictRedis(host='localhost', port=6379, db=0)


def categories(request):
    if request.method == "GET":
        all_serials = Serial.objects.filter(published=True)
        link = 'serials:categories'
        name = 'categories'
        request, context = filters_serials(request, all_serials, link, name)
        return render(request, 'serials/categories.html', context=context)
    else:
        all_serials = Serial.objects.filter(published=True).order_by('-rating')
        page_serials = Paginator(all_serials, 50).page(1)
        return render(request, 'serials/categories.html',
                      {'context': 'categories', 'zapros': "все сериалы", 'page_serials': page_serials, "page": 0})


def info(request):
    # Вывод онформации о сериале
    if request.method == "GET":
        slug = request.GET.get("name")
        serial = get_object_or_404(Serial, published=True, slug=slug)
        serial_info = Serial_info.objects.filter(serial=serial.id)
        # Загружает дополнительную информацию с сайта MySeria, если такая есть
        if serial_info.exists():
            serial_info = serial_info[0]
        else:
            serial_info = save_serial_info(serial)
        if serial.posterImage.name == '':
            if serial.posterLink != "No_poster" and serial.posterLink != "User_image":
                image = requests.get(serial.posterLink).content
                img = io.BytesIO(image)
                serial.posterImage.save(f'{serial.slug}.img', img, save=True)
        redis_instance.zincrby('serial_ranking', 1, serial.slug)
        similar_serials = similar_serials_ret(serial)

        if request.user.is_authenticated:
            profile = get_object_or_404(Profile, user=request.user.id)
            if serial.slug in [i.slug for i in profile.liked_serials.all()]:
                like = 'unlike'
            else:
                like = 'like'
            return render(request, 'serials/info.html',
                          {'serial': serial, 'serial_info': serial_info, "similar_serials": similar_serials,
                           'like': like})
        return render(request, 'serials/info.html',
                      {'serial': serial, 'serial_info': serial_info, "similar_serials": similar_serials})
    # Обновляет дополнительную информацию с сайта MySeria, если такая есть
    elif request.method == "POST":
        slug = request.POST.get("slug")
        like = request.POST.get("like")
        if request.user.is_authenticated and like is not None:
            serial = get_object_or_404(Serial, published=True, slug=slug)
            serial_info = get_object_or_404(Serial_info, serial=serial.id)
            profile = get_object_or_404(Profile, user=request.user.id)
            if like == 'like' and not profile.liked_serials.filter(slug=slug).exists():
                profile.liked_serials.add(serial)
                for i in [i.slug for i in serial.genres.all()]:
                    redis_instance.zincrby(f'{profile.user.id}_reccomend', 1, i)
                like = 'unlike'
            elif like == 'like' and profile.liked_serials.filter(slug=slug).exists():
                like = 'unlike'
            elif like == 'unlike' and profile.liked_serials.filter(slug=slug).exists():
                profile.liked_serials.remove(serial)
                for i in [i.slug for i in serial.genres.all()]:
                    redis_instance.zincrby(f'{profile.user.id}_reccomend', -1, i)
                like = 'like'
            elif like == 'unlike' and not profile.liked_serials.filter(slug=slug).exists():
                like = 'like'
            similar_serials = similar_serials_ret(serial)
            return render(request, 'serials/info.html',
                          {'serial': serial, 'serial_info': serial_info, "similar_serials": similar_serials,
                           'like': like})

        else:
            serial = get_object_or_404(Serial, published=True, slug=slug)
            if request.user.is_authenticated:
                profile = get_object_or_404(Profile, user=request.user.id)
                if serial.slug in [i.slug for i in profile.liked_serials.all()]:
                    like = 'unlike'
                else:
                    like = 'like'
            else:
                like = 'like'
            if serial.serialYearEnd == 9999:
                serial_info = save_serial_info(serial)
            else:
                # serial_info = save_serial_info(serial)
                serial_info = get_object_or_404(Serial_info, serial=serial.id)
            similar_serials = similar_serials_ret(serial)
            return render(request, 'serials/info.html',
                          {'serial': serial, 'serial_info': serial_info, "similar_serials": similar_serials, 'like': like})
    else:
        return HttpResponseNotFound(
            '<h1>Ошибка запроса, возможно вы пытаеть получить информацию так, как это не предполагается</h1>')


def home(request):
    return redirect(reverse('serials:categories'))


def popular_serials(request):
    page = request.GET.get('page')
    # Получаем набор рейтинга сериалов.
    serial_ranking = redis_instance.zrange('serial_ranking', 0, -1, desc=True)[:200]
    serial_ranking_slugs = [slug.decode("utf-8") for slug in serial_ranking]
    # Получаем отсортированный список самых популярных сериалов.
    most_viewed = list(Serial.objects.filter(published=True).filter(slug__in=serial_ranking_slugs))
    most_viewed.sort(key=lambda x: serial_ranking_slugs.index(x.slug))
    if page is None:
        page = 1
    serials = Paginator(most_viewed, 50)
    try:
        page_serials = serials.page(page)
    except PageNotAnInteger:
        # Если страница не является целым числом, возвращаем первую страницу.
        page_serials = serials.page(1)
    except EmptyPage:
        # Если номер страницы больше, чем общее количество страниц, возвращаем последнюю.
        page_serials = serials.page(serials.num_pages)
    return render(request, 'serials/categories.html',
                  {'context': 'top', 'page_serials': page_serials, "page": ((int(page) - 1) * 50),
                   'link': 'serials:popular'})


# Выводит (и сохраняет в бд) дополнительную информацию
def save_serial_info(serial):
    if serial.pk == 631:
        otvet = proverka_serials("Неуязвимый", str(serial.serialYearStart))
    elif serial.pk == 2212:
        otvet = proverka_serials(serial.title, str(1997))
    elif serial.pk == 500:
        otvet = proverka_serials("Любовь, смерть и роботы", str(serial.serialYearStart))
    elif serial.pk == 3635:
        otvet = proverka_serials("ВандаВижн", str(serial.serialYearStart))
    else:
        otvet = proverka_serials(serial.title, str(serial.serialYearStart))
    if otvet:
        serial_info = Serial_info(serial=serial, MySeriadescription=otvet.get('description'),
                                  MySeriarating=otvet.get('rating'), LastSerianame=otvet.get('last_seria'),
                                  LastSeriaurl=otvet.get('last_seria_url'), LastSeriavoice=otvet.get('voices'))
    else:
        serial_info = Serial_info(serial=serial, MySeriadescription="Нет описания",
                                  MySeriarating=0, LastSerianame="Сериал отсутсвует",
                                  LastSeriaurl="#", LastSeriavoice="-")
    serial_info.save()
    return serial_info


def similar_serials_ret(serial):
    # Формирование списка похожих сериалов.
    serial_genres_ids = serial.genres.values_list('id', flat=True)
    similar_serials = Serial.objects.filter(published=True).filter(genres__in=serial_genres_ids).exclude(
        id=serial.id)
    similar_serials = similar_serials.annotate(same_tags=Count('genres')) \
                          .order_by('-same_tags', '-rating')[:10]
    return similar_serials


# Загружает дополнительную информацию с сайта MySeria, если такая есть
def proverka_serials(serial, yearStart):
    try:
        vihod = {}
        host = "http://myseria.pro"
        user_ag = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36'
        otvet = [[], [], []]
        with requests.Session() as sess:
            s = serial.split()
            story = "+".join(s)
            url = f'{host}/?do=search&subaction=search&story={story}'
            responce = sess.get(url=url, headers={'user-agent': user_ag})
            soup = BeautifulSoup(responce.text, "lxml")
            result = soup.find_all('div', class_='item-search-serial')
            if len(result) == 1:
                if result[0].find('div', class_='item-search-header').find('a').text.lower() == serial.lower():
                    otvet[2] = result[0].find('div', class_='item-search-header').find('a').get('href')
                else:
                    otvet[1] = serial
            elif len(result) == 0:
                otvet[1] = serial
            elif len(result) > 1:
                c = 0
                for item in result:
                    if item.find('div', class_='item-search-header').find('a').text.lower() == serial.lower():
                        c = 1
                        break
                if c == 1:
                    otvet[2] = result[0].find('div', class_='item-search-header').find('a').get('href')
                else:
                    otvet[1] = serial
            if len(otvet[2]) != 0:
                responce2 = sess.get(url=otvet[2], headers={'user-agent': user_ag})
                soup2 = BeautifulSoup(responce2.text, "lxml")
                infoMySeria = soup2.find('div', class_='serial-page-desc single')
                topMySeria = infoMySeria.find('div', class_='small-12 medium-7 large-6 columns').find('ul',
                                                                                                      class_='info-list').find_all(
                    'div', class_='field-text')
                for_search = infoMySeria.find('div', class_='small-12 medium-7 large-6 columns').find('ul',
                                                                                                      class_='info-list').find_all(
                    'div', class_='field-label')
                for_search2 = 4
                for_search3 = 2
                for index, i in enumerate(for_search):
                    if i.text == "Год:":
                        for_search2 = index
                    if i.text == "Наш рейтинг:":
                        for_search3 = index
                if topMySeria[for_search2].text[:4] == yearStart:
                    vihod["description"] = infoMySeria.find('div', class_='cat-desc-serial').find('div',
                                                                                                  class_='body').text
                    for_rating = topMySeria[for_search3].find('div', class_='rating').find('meta',
                                                                                           itemprop='ratingValue')
                    if for_rating is None:
                        vihod["rating"] = 0
                    else:
                        vihod["rating"] = float(for_rating.get('content').replace(",", "."))
                    req_serial = requests.get(otvet[2])
                    soup_serial = BeautifulSoup(req_serial.text, 'lxml')
                    last_seria_link = soup_serial.find('div', class_="page-content").find("div",
                                                                                          class_="item-serial").find(
                        "div", class_="field-title").find("a").get("href")
                    req_seria = requests.get(last_seria_link)
                    soup_seria = BeautifulSoup(req_seria.text, 'lxml')
                    vihod["last_seria"] = soup_seria.find("div", class_="title-links-wrapper clearfix").find("div",
                                                                                                             class_="gap-correct").find(
                        'h1').text
                    vihod["last_seria_url"] = last_seria_link
                    voices = soup_seria.find("div", class_="sounds-wrapper").find("div", class_="sounds-list").find_all(
                        "div")
                    voi_vih = []
                    for i in voices:
                        voi_vih.append(i.text)
                    vihod["voices"] = ", ".join(voi_vih)
                else:
                    return False
        return vihod
    except Exception as e:
        print(e)
        return False
