from django.conf.urls.static import static
from django.urls import path, include
from django.conf import settings

from .views import *

urlpatterns = [
    path('courses/<str:crs>', course_with_compiler, name='course_with_compiler'),
    path('courses/', course_list, name='course_list'),
    path('my-courses/', my_courses_view, name='my_courses'),
    path('<int:course_id>/', course_detail, name='course_detail'),  
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)