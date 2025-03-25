from django.conf.urls.static import static
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import *

urlpatterns = [
    path('logout/', logout_view, name='logout'),
    path('profile/', login_view, name='profile'),
    path('register/', RegisterUser.as_view(), name='register'),
    path('', include('Main.urls')),
    path("settings/", settings_view, name="settings"),
    path("help/", help_view, name="help"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)