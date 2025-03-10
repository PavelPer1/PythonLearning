import os
from sqlite3 import IntegrityError

from django.shortcuts import render, get_object_or_404
from Courses.models import StudentCourser, Courses
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from PythonLearning import settings


import json
import traceback
from io import StringIO
from contextlib import redirect_stdout
from Courses.models import Courses, StudentCourser
from Profile.models import Student

def my_courses_view(request):
    my_crs = []
    for i in StudentCourser.objects.all():
        if i.student.name == request.user:
            my_crs.append(i.courses)

    return render(request, 'my_courses.html', {'my_crs': my_crs})


def course_list(request):
    my_crs = []
    crs = Courses.objects.all()  # Получаем все курсы

    # Получаем параметры поиска и сортировки из GET-запроса
    search_query = request.GET.get('search', '')  
    sort_by = request.GET.get('sort', 'name')  

    # Фильтруем курсы по названию
    if search_query:
        crs = crs.filter(name__icontains=search_query)

    # Применяем сортировку
    if sort_by == 'name':
        crs = crs.order_by('name')
    elif sort_by == 'author':
        crs = crs.order_by('author')
    elif sort_by == 'language':
        crs = crs.order_by('language')

    # Проверяем, на какие курсы подписан пользователь
    for i in StudentCourser.objects.all():
        if i.student.name == request.user:
            my_crs.append(i.courses)

    # Обработка подписки на курс
    if request.method == "POST":
        course_id = request.POST.get('course_id')
        try:
            course = Courses.objects.get(id=int(course_id))
            student = Student.objects.get(name=request.user)
            if student and not StudentCourser.objects.filter(student=student, courses=course).exists():
                StudentCourser(courses=course, student=student).save()
        except Courses.DoesNotExist:
            print('Курс не найден')
        except Exception as e:
            print(f"Произошла ошибка: {e}")
        return redirect(request.path_info)

    return render(request, 'course_list.html', {
        'courses': crs,
        'my_crs': my_crs,
        'search_query': search_query,
        'sort_by': sort_by,
    })

def course_detail(request, course_id):
    course = get_object_or_404(Courses, id=course_id)  # Получаем курс по ID
    students_count = StudentCourser.objects.filter(courses=course).count()  # Количество учеников на курсе

    return render(request, 'course_detail.html', {'course': course, 'students_count': students_count})



def execute_code_safely(code):
    try:
        local_globals = {
            '__builtins__': {
                'print': print,
                'len': len,
                'range': range,
                'sum': sum,
                'min': min,
                'max': max,
                'abs': abs,
                'str': str,
                'int': int,
                'float': float,
                'dict': dict,
                'list': list,
                'tuple': tuple,
            },
            '__name__': '__main__',
        }

        output_buffer = StringIO()
        with redirect_stdout(output_buffer):
            exec(code, local_globals)

        output = output_buffer.getvalue()

        if not output:
            last_result = local_globals.get('_', None)
            if last_result is not None:
                output = str(last_result)

        return output if output else "Program executed without output."

    except SyntaxError as e:
        return f"SyntaxError: {e.msg}"  # Оставляем только краткое сообщение
    except Exception as e:
        return f"{type(e).__name__}: {e}"  # Остальные ошибки тоже без трассировки

def course_with_compiler(request, crs):
    course = get_object_or_404(Courses, name=crs)
    output = None
    code = ""
    tasks = course.data

    task_completed = False

    if request.method == "POST":
        code = request.POST.get('codearea', '')

        if len(code) > 1000:
            return HttpResponse("Code is too long", status=400)

        output = execute_code_safely(code)
        task_id = request.POST.get('task_id', '')

    context = {
        'courses': course,
        'output': output,
        'code': code,
        'tasks_json': tasks,  # Преобразуем в JSON-строку
        'task_completed': task_completed,
    }

    return render(request, 'get_courses.html', context)
