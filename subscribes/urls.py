from django.urls import path

from . import views

app_name = 'subscribes'

urlpatterns = [
    path("subscribe/", views.subscribe, name='subscribe'),
    path("recommend/", views.recommend, name='recommend')
]
