from django.urls import path

from . import views

app_name = 'controls'

urlpatterns = [
    path('add/', views.AddSerial.as_view(), name='add_serials'),
    path('delete/<slug:slug>/', views.DeleteSerial.as_view(), name='delete'),
    path('all/', views.ListSerials.as_view(), name='all'),
    path('edit/<slug:slug>/', views.EditSerial.as_view(), name='edit'),
    # path('tags_slug_update/', views.tags_slug_update, name='tags_slug_update'),
    # Полностью обновляет базу данных, основываясь на json файле
    # path('create_base/', views.create_base, name='create_base'),
]
