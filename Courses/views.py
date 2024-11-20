

from django.shortcuts import render

from Courses.models import StudentCourser


def render_courses(request):
    my_courses = []
    for i in StudentCourser.objects.all():
        if request.user.id == i.student.name.id:
            my_courses += [i.courses.name]
    print(my_courses)
    context = {
        'my_courses': my_courses
    }
    return render(request, 'user_courses.html', context=context)
