from django.contrib.postgres.search import TrigramSimilarity
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import Http404
from django.shortcuts import get_object_or_404
from taggit.models import Tag

ORDERS = [('Название(А-Я)', 'title'), ('Название(Я-А)', '-title'), ('Рейтинг(+)', 'rating'),
          ('Рейтинг(-)', '-rating'),
          ('Год выхода(+)', 'serialYearStart'), ('Год выхода(-)', '-serialYearStart'),
          ('Год закрытия(+)', 'serialYearEnd'), ('Год закрытия(-)', '-serialYearEnd'),
          ('Страна(А-Я)', 'countries'),
          ('Страна(Я-А)', '-countries')]


def filters_serials(request, all_serials, link, context):
    try:
        # Извлечение информации из запроса
        vihod = ""
        page = request.GET.get('page')
        cat = request.GET.get('category')
        order_by = request.GET.get('order_by')
        yearStart = request.GET.get('yearStart')
        yearEnd = request.GET.get('yearEnd')
        search = request.GET.get('search')
        # Если это запрос на поиск сериала, то идёт поиск только по названию
        if search is not None:
            all_serials = all_serials.annotate(similarity=TrigramSimilarity('title', search),
                                               ).filter(similarity__gt=0.3).order_by('-similarity',
                                                                                     '-serialYearStart')
            cat = f'{search}'
            vihod += f"&search={search}"
            zapros = [f"{cat}"]
        # Если в заголовке нет информации о поиске сериала, то применяются остальные фильтры
        else:
            if cat is not None:
                if cat != 'all':
                    genres = get_object_or_404(Tag, slug=cat)
                    all_serials = all_serials.filter(genres__in=[genres])
                    vihod += f"&category={cat}"
                    cat = genres.name
                else:
                    cat = "все"
            else:
                cat = "все"
            if order_by is not None:
                all_serials = all_serials.order_by(order_by)
                vihod += f"&order_by={order_by}"
                sort = ", ".join([i[0] for i in ORDERS if i[1] == order_by])
            elif order_by is None and link == "subscribes:subscribe":
                sort = "По порядку добавления"
            else:
                all_serials = all_serials.order_by("-rating")
                sort = 'Рейтинг(-)'
            if yearStart is not None:
                all_serials = all_serials.filter(serialYearStart__gte=int(yearStart))
                vihod += f"&yearStart={yearStart}"
            else:
                yearStart = "любой"
            if yearEnd is not None:
                all_serials = all_serials.filter(serialYearEnd__lte=int(yearEnd))
                vihod += f"&yearEnd={yearEnd}"
            zapros = [f"категория: {cat}", f"сортировка: {sort}", f"год: {yearStart}"]
        if page is None:
            page = 1

        serials = Paginator(all_serials, 50)
        try:
            page_serials = serials.page(page)
        except PageNotAnInteger:
            # Если страница не является целым числом, возвращаем первую страницу.
            page_serials = serials.page(1)
        except EmptyPage:
            # Если номер страницы больше, чем общее количество страниц, возвращаем последнюю.
            page_serials = serials.page(serials.num_pages)
        return [request, {'context': context, 'zapros': zapros, 'page_serials': page_serials,
                          "page": ((int(page) - 1) * 50), "vihod": vihod, 'link': link}]
    except:
        raise Http404("Выбранные фильтры не применимы.")
