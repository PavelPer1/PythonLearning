from django.conf.urls.static import static
from django.urls import path, include
from .views import *

urlpatterns = [
    path('main/', render_main_title, name='main_title'),  # Добавляем завершающий слэш
    path('', render_main_title, name='home'),  # Указываем render_main_title для корня сайта
    path('main/create_course', include('Courses.urls'), name='create_course'),
    path('', include('Courses.urls'))  # Перенос маршрутов Courses на /courses/
]
