from sqlite3 import IntegrityError

from django.shortcuts import render, get_object_or_404
from Courses.models import StudentCourser, Courses
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

import json
import traceback
from io import StringIO
from contextlib import redirect_stdout
from Courses.models import Courses, StudentCourser
from Profile.models import Student


def course_list(request):
    my_crs = []
    crs = Courses.objects.all()  # Получаем все курсы

    for i in StudentCourser.objects.all():
        if i.student.name == request.user:
            my_crs += [i.courses]
    if request.method == "POST":
        course_id = request.POST.get('course_id')
        try:
            for i in crs:
                print(i.id, int(course_id))
            course = Courses.objects.get(id=int(course_id))
            student = Student.objects.get(name=request.user)
            if student:
                # Проверка на существование записи
                if not StudentCourser.objects.filter(student=student, courses=course).exists():
                    StudentCourser(courses=course, student=student).save()
                else:
                    print('Запись уже существует')  # В продакшене - сообщение пользователю
            else:
                print("У пользователя нет связанного студента!")  # Обработка ошибки
        except Courses.DoesNotExist:
            print('Курс не найден')  # Обработка ошибки
        except Exception as e:
            print(f"Произошла ошибка: {e}")  # Обработка ошибок
        return redirect(request.path_info)
    return render(request, 'course_list.html', {'courses': crs, 'my_crs': my_crs})




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
    tasks = {
        "task1": {"title": "Задание 1", "description": "Описание задания 1", "expected_output": "Hello World"},
        "task2": {"title": "Задание 2", "description": "Описание задания 2", "expected_output": "Goodbye World"},
        "task3": {"title": "Задание 3", "description": "Описание задания 3", "expected_output": "Hello Python"},
        "task4": {"title": "Задание 4", "description": "Описание задания 4", "expected_output": "Welcome to Python"},
    }
    task_completed = False  # Переменная для проверки, выполнено ли задание

    if request.method == "POST":
        code = request.POST.get('codearea', '')

        if len(code) > 1000:
            return HttpResponse("Code is too long", status=400)

        output = execute_code_safely(code)
        task_id = request.POST.get('task_id', '')
        if task_id and tasks.get(task_id) and output.strip() == tasks[task_id]["expected_output"]:
            task_completed = True

    context = {
        'courses': course,
        'output': output,
        'code': code,
        'tasks_json': json.dumps(tasks),  # Передаем JSON с заданиями в шаблон
        'task_completed': task_completed,  # Передаем статус выполнения задания
    }

    return render(request, 'get_courses.html', context)
