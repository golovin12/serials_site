from django.urls import path
from . import views


app_name = 'serials'

urlpatterns = [
    path('categories/', views.categories, name='categories'),
    path('info/', views.info, name='info'),
    path('home/', views.home, name='home'),
    path('popular/', views.popular_serials, name='popular'),
]
