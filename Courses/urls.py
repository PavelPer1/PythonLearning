from django.conf.urls.static import static
from django.urls import path, include

from .views import *

urlpatterns = [
    path('courses',render_courses, name='user_courses'),
    path('courses/<crs>', get_courses, name='courses')
]
