from django.urls import path

from . import views

app_name = 'controls'

urlpatterns = [
    path('update/', views.update_serials, name='update_serials'),
    path('update/all/', views.update_all, name='update_all'),
    path('update/last/', views.update_last, name='update_last'),
    path('add/', views.add_serials, name='add_serials'),
    path('delete/', views.delete_serials, name='delete_serials'),
    # path('tags_slug_update/', views.tags_slug_update, name='tags_slug_update'),
    # Полностью обновляет базу данных, основываясь на json файле
    # path('create_base/', views.create_base, name='create_base'),
]
