from django.conf.urls.static import static
from django.urls import path, include

from .views import *

urlpatterns = [
    path('profile', login_view, name='profile'),
    path('register/', RegisterUser.as_view(), name='register'),
]
