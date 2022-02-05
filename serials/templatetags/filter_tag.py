from django import template
from taggit.models import Tag

from ..forms import Search_Form

register = template.Library()


@register.simple_tag(name='search_form')
def search_form():
    return Search_Form()


TAGS = ["Жанр", "category", [(i.name, i.slug) for i in Tag.objects.all().order_by("name")]]
ORDERS = ["Сортировка", "order_by",
          [('Название(А-Я)', 'title'), ('Название(Я-А)', '-title'), ('Рейтинг(+)', 'rating'),
           ('Рейтинг(-)', '-rating'),
           ('Год выхода(+)', 'serialYearStart'), ('Год выхода(-)', '-serialYearStart'),
           ('Год закрытия(+)', 'serialYearEnd'), ('Год закрытия(-)', '-serialYearEnd'),
           ('Страна(А-Я)', 'countries'),
           ('Страна(Я-А)', '-countries')]]
YEARS = ["Год выхода", "yearStart",
         [('2022', '2022'), ('2021', '2021'), ('2020', '2020'), ('2019', '2019'), ('2018', '2018'),
          ('2015', '2015'),
          ('2010', '2010'), ('2005', '2005'), ('2000', '2000'), ('1990', '1990'), ('1980', '1980'),
          ('1950', '1950')]]


@register.inclusion_tag('serials/filter_form.html')
def filter_form(vihod=None, link='serials:categories', filt=3):
    return {'formes': [TAGS, ORDERS, YEARS][:filt], 'vihod': vihod, 'link': link}
