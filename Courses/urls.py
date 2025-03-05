from django.conf.urls.static import static
from django.urls import path, include

from .views import *

urlpatterns = [
    path('courses/<str:crs>', course_with_compiler, name='course_with_compiler'),
    path('courses/', course_list, name='course_list'),

]
