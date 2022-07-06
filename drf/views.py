from django.contrib.postgres.search import TrigramSimilarity
from rest_framework.authentication import SessionAuthentication
from rest_framework.filters import OrderingFilter, BaseFilterBackend
from rest_framework.generics import ListAPIView, get_object_or_404, RetrieveAPIView, CreateAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import BasePermission
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from taggit.models import Tag

from serials.models import Serial, Serial_info
from .serializers import SerialSerializer, SerialInfoSerializer, SerialsSerializer


# Класс для проверки принадлежности пользователя к админу
class AdminPermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name="Admin_for_site").exists()


# Класс для пагинации
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 100


# Класс для поиска с помощью триграм
class SearchSerialsFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        search = request.GET.get('search')
        if search is not None:
            queryset = queryset.annotate(similarity=TrigramSimilarity('title', search),
                                         ).filter(similarity__gt=0.3).order_by('-similarity',
                                                                               '-serialYearStart')
        return queryset


# Класс для фильтрации по жанрам
class GenresFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        genr = request.GET.get('genres')
        if genr is not None:
            genres = get_object_or_404(Tag, slug=genr)
            queryset = queryset.filter(genres__in=[genres])
        return queryset


# Класс с основными параметрами, которые должны быть применены
class BaseSerialsMixin:
    authentication_classes = [SessionAuthentication]
    permission_classes = [AdminPermission]


# Выводит список сериалов
class SerialsList(BaseSerialsMixin, ListAPIView):
    queryset = Serial.objects.filter(published=True).prefetch_related("genres")
    pagination_class = StandardResultsSetPagination
    serializer_class = SerialsSerializer
    filter_backends = [OrderingFilter, SearchSerialsFilter, GenresFilter]
    ordering_fields = ['title', 'rating', 'serialYearStart', 'serialYearEnd', 'countries']
    ordering = ['-rating']
    template_name = 'api/list.html'
    # renderer_classes = [TemplateHTMLRenderer]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response({"serials": serializer.data, "info": "info"})
        serializer = self.get_serializer(queryset, many=True)
        return Response({"serials": serializer.data, "info": "info"})


# Выводит информацию о сериале
class SerialInfo(BaseSerialsMixin, RetrieveAPIView):
    serializer_class = SerialSerializer
    queryset = Serial.objects.filter(published=True).prefetch_related("genres").select_related('serial_info')
    lookup_field = 'slug'
    lookup_url_kwarg = 'slug'
    template_name = 'api/detail.html'
    renderer_classes = [TemplateHTMLRenderer]


class SerialAdd(BaseSerialsMixin, CreateAPIView):
    model = Serial
    serializer_class = SerialSerializer
    def get(self, request, *args, **kwargs):
        return super().options(request, *args, *kwargs)


