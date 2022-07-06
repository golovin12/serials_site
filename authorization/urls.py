from django.contrib.auth import views as auth_views
from django.urls import path, include, reverse_lazy

from . import views

app_name = 'authorization'

urlpatterns = [
    path('password_reset/',
         auth_views.PasswordResetView.as_view(success_url=reverse_lazy('authorization:password_reset_done')),
         name='password_reset'),
    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(success_url=reverse_lazy('authorization:password_reset_complete')),
         name='password_reset_confirm'),
    path('password_change/',
         auth_views.PasswordChangeView.as_view(success_url=reverse_lazy('authorization:password_change_done')),
         name='password_change'),
    path('', include('django.contrib.auth.urls')),
    path('register/', views.register, name='register'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
]
