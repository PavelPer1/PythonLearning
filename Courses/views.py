import os
from sqlite3 import IntegrityError

import json
from django.http import JsonResponse
from .forms import CourseForm

from django.shortcuts import render, get_object_or_404
from Courses.models import StudentCourser, Courses
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from PythonLearning import settings
from django.views.decorators.csrf import csrf_exempt

import json
import traceback
from io import StringIO
from contextlib import redirect_stdout
from Courses.models import Courses, StudentCourser, CompletedTask
from Profile.models import Student, Teacher
from django.http import JsonResponse


def my_courses_view(request):
    my_crs = []
    for i in StudentCourser.objects.all():
        if i.student.name == request.user:
            my_crs.append(i.courses)

    teach = False

    if request.user.is_authenticated:
        teach = Teacher.objects.filter(name=request.user).exists()

    context = {
        'teacher': teach,
        'my_crs': my_crs
    }

    return render(request, 'my_courses.html', context)


def course_list(request):
    my_crs = []
    crs = Courses.objects.all()  # Получаем все курсы

    # Получаем параметры поиска и сортировки из GET-запроса
    search_query = request.GET.get('search', '')  
    sort_by = request.GET.get('sort', 'name')

    teach = False

    if request.user.is_authenticated:
        teach = Teacher.objects.filter(name=request.user).exists()

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
        'teacher': teach

    })

def course_detail(request, course_id):
    course = get_object_or_404(Courses, id=course_id)  # Получаем курс по ID
    students_count = StudentCourser.objects.filter(courses=course).count()  # Количество учеников на курсе
    tasks_json = course.data  # Добавляем JSON-данные о модулях
    my_crs = []
    for i in StudentCourser.objects.all():
        if i.student.name == request.user:
            my_crs.append(i.courses)
    return render(request, 'course_detail.html', {
        'course': course,
        'students_count': students_count,
        'tasks_json': tasks_json,
        'my_crs': my_crs  # Передаем модули на страницу

    })



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
                'type': type
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

# ... (остальные импорты остаются без изменений)

def course_with_compiler(request, crs):
    course = get_object_or_404(Courses, name=crs)
    output = None
    code = ""
    tasks = course.data

    task_completed = False
    teach = False

    if request.user.is_authenticated:
        teach = Teacher.objects.filter(name=request.user).exists()

    if request.method == "POST":
        code = request.POST.get('codearea', '')
        task_id = request.POST.get('task_id', '')

        if len(code) > 1000:
            return HttpResponse("Code is too long", status=400)

        output = execute_code_safely(code)

        # Проверяем правильность выполнения задания
        correct_answer = None
        for module in tasks['modules']:
            for section in module['sections']:
                for content in section['contents']:
                    if content['type'] == 'practice' and content['title'] == task_id:
                        correct_answer = content.get('answer')
                        break

        if correct_answer is not None and output.strip() == correct_answer.strip():
            task_completed = True
            # Сохраняем прогресс
            student = Student.objects.filter(name_id=request.user.id).first()
            if student:
                CompletedTask.objects.get_or_create(student=student, course=course, task_id=task_id)
    tasks_json_str = json.dumps(tasks, ensure_ascii=False)

    context = {
        'courses': course,
        'output': output,
        'code': code,
        'tasks_json': tasks,
        'task_completed': task_completed,
        'teacher': teach,
        'tasks_json': tasks,             # если ты где-то используешь как объект
        'tasks_json_str': tasks_json_str  # для <script>
    }

    return render(request, 'get_courses.html', context)

