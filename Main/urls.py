from django.conf.urls.static import static
from django.urls import path, include

from .views import *

urlpatterns = [
    path('main', render_main_title, name='main_title'),
]
