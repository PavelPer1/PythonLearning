from django.contrib import admin

from Courses.models import Courses, StudentCourser, CompletedTask

admin.site.register(Courses)
admin.site.register(StudentCourser)
admin.site.register(CompletedTask)
