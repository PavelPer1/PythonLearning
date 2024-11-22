from django.shortcuts import render

from Courses.models import StudentCourser, Courses


def render_courses(request):
    my_courses = []
    for i in StudentCourser.objects.all():
        if request.user.id == i.student.name.id:
            my_courses += [i.courses.name]
    context = {
        'my_courses': my_courses
    }
    return render(request, 'user_courses.html', context=context)

def get_courses(request, crs):
    courses = Courses.objects.get(name=crs)

    context = {
        'courses': courses
    }

    return render(request, 'get_courses.html', context=context)