import redis
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count
from django.http import Http404
from django.shortcuts import render, get_object_or_404

from authorization.models import Profile
from serials.filters_serials import filters_serials
from serials.models import Serial

redis_instance = redis.StrictRedis(host='localhost', port=6379, db=0)


@login_required
def subscribe(request):
    profile = get_object_or_404(Profile, user__username=request.user.username)
    liked_serials = profile.liked_serials.all().filter(published=True)
    if liked_serials.count() == 0:
        raise Http404("У вас нет понравившихся сериалов.")
    link = 'subscribes:subscribe'
    name = 'subscribe'
    request, context = filters_serials(request, liked_serials, link, name)
    return render(request, "serials/categories.html", context=context)


@login_required
def recommend(request):
    page = request.GET.get('page')
    profile = Profile.objects.get(user_id=request.user.id)
    if profile.liked_serials.all().exists():
        genres_ranking = redis_instance.zrange(f'{request.user.id}_reccomend', 0, -1, desc=True)[:3]
        genres_ranking_slugs = [slug.decode("utf-8") for slug in genres_ranking]
        if len(genres_ranking_slugs) != 0:
            serials = Serial.objects.all()
            similar_serials = serials.filter(published=True).filter(genres__slug__in=genres_ranking_slugs).exclude(
                id__in=[i.id for i in profile.liked_serials.all()])
            similar_serials = similar_serials.annotate(same_tags=Count('genres')) \
                                  .order_by('-same_tags', '-rating')[:200]
            if page is None:
                page = 1
            serials = Paginator(similar_serials, 50)
            try:
                page_serials = serials.page(page)
            except PageNotAnInteger:
                # Если страница не является целым числом, возвращаем первую страницу.
                page_serials = serials.page(1)
            except EmptyPage:
                # Если номер страницы больше, чем общее количество страниц, возвращаем последнюю.
                page_serials = serials.page(serials.num_pages)
            return render(request, "serials/categories.html", {'context': 'recommend', 'page_serials': page_serials,
                                                               "page": ((int(page) - 1) * 50),
                                                               'link': 'subscribes:recommend'})
    else:
        raise Http404("У вас нет понравившихся сериалов.")
