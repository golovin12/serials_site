from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from serials import views as serials_view
from . import views

urlpatterns = [
    path('', serials_view.home, name='home'),
    path('authorization/', include('authorization.urls', namespace='authorization')),
    path('subscribes/', include('subscribes.urls', namespace='subscribes')),
    path('serials/', include('serials.urls', namespace='serials')),
    path('controls/', include('controls.urls', namespace='controls')),
    path('__debug__/', include('debug_toolbar.urls')),
]


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

handler500 = views.m500
handler410 = views.m410
handler405 = views.m405
handler404 = views.m404
handler403 = views.m403
handler400 = views.m400
handler304 = views.m304