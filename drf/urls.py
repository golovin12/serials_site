from django.urls import path
from . import views


app_name = 'api'

urlpatterns = [
    path('serials/', views.SerialsList.as_view(), name='serials'),
    path('serials/add/', views.SerialAdd.as_view(), name='add'),
    path('serials/<slug:slug>/', views.SerialInfo.as_view(), name='info'),
]