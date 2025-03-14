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

@csrf_exempt
@login_required
def save_progress(request):
    """Сохраняем выполненное задание и проверяем правильность ответа."""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            task_id = data.get("task_id")
            course_id = data.get("course_id")
            student, created = Student.objects.get_or_create(name_id=request.user.id)
            course = Courses.objects.filter(id=course_id).first()

            if not course:
                return JsonResponse({"error": "Курс не найден"}, status=400)

            # Получаем задание и правильный ответ
            task = Task.objects.filter(id=task_id).first()
            if not task:
                return JsonResponse({"error": "Задание не найдено"}, status=400)

            correct_answer = task.answer  # Предположим, что в модели Task есть поле "answer" с правильным ответом
            user_answer = data.get("code")

            # Проверяем правильность ответа
            if user_answer.strip() == correct_answer.strip():
                is_correct = True
            else:
                is_correct = False

            # Сохраняем прогресс
            CompletedTask.objects.get_or_create(student=student, course=course, task_id=task_id)

            return JsonResponse({"message": "Прогресс сохранён!", "is_correct": is_correct}, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


@login_required
def get_progress(request, course_id):
    """Получаем список выполненных заданий для курса."""
    student = Student.objects.filter(name_id=request.user.id).first()
    
    if not student:
        return JsonResponse({"completed_tasks": []}, status=200)

    completed_tasks = CompletedTask.objects.filter(student=student, course_id=course_id).values_list("task_id", flat=True)
    return JsonResponse({"completed_tasks": list(completed_tasks)}, status=200)

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

def course_with_compiler(request, crs):
    course = get_object_or_404(Courses, name=crs)
    output = None
    code = ""
    tasks = course.data

    task_completed = False

    if request.method == "POST":
        code = request.POST.get('codearea', '')
        task_id = request.POST.get('task_id', '')

        if len(code) > 1000:
            return HttpResponse("Code is too long", status=400)

        output = execute_code_safely(code)

        # Получаем правильный ответ для текущей задачи
        correct_answer = None
        for module in tasks['modules']:
            for section in module['sections']:  # Изменено на 'sections'
                for task in section['tasks']:  # Изменено на 'tasks'
                    if task['title'] == task_id:  # Предполагаем, что task_id соответствует заголовку задания
                        correct_answer = task.get('answer')
                        break

        # Проверяем, совпадает ли вывод с правильным ответом
        if correct_answer is not None:
            if output.strip() == correct_answer.strip():
                task_completed = True
        else:
            print(f"Правильный ответ не найден для task_id: {task_id}")

    context = {
        'courses': course,
        'output': output,
        'code': code,
        'tasks_json': tasks,  # Преобразуем в JSON-строку
        'task_completed': task_completed,
    }

    return render(request, 'get_courses.html', context)


def render_create_course(request):
    if request.method == 'POST':
        # Соберите данные из формы
        course_data = {
            "title": request.POST.get('course_title'),
            "description": request.POST.get('course_description'),
            "modules": []
        }

        module_count = 1
        while True:
            module_title = request.POST.get(f'module_title_{module_count}')
            if not module_title:
                break  # Прекратите, если модуль не найден

            module_description = request.POST.get(f'module_description_{module_count}')
            module = {
                "title": module_title,
                "description": module_description,
                "sections": []  # Изменено на "sections"
            }

            section_count = 1
            while True:
                section_title = request.POST.get(f'section_title_{module_count}_{section_count}')
                if not section_title:
                    break  # Прекратите, если раздел не найден

                section_description = request.POST.get(f'section_description_{module_count}_{section_count}')
                section = {
                    "title": section_title,
                    "description": section_description,
                    "tasks": []  # Изменено на "tasks"
                }

                task_count = 1
                while True:
                    task_title = request.POST.get(f'task_title_{module_count}_{section_count}_{task_count}')
                    if not task_title:
                        break  # Прекратите, если задание не найдено

                    task_description = request.POST.get(f'task_description_{module_count}_{section_count}_{task_count}')
                    task_answer = request.POST.get(f'task_answer_{module_count}_{section_count}_{task_count}')

                    task = {
                        "title": task_title,
                        "description": task_description,
                        "answer": task_answer  # Добавлено поле для ответа
                    }

                    section["tasks"].append(task)  # Добавляем задание в раздел
                    task_count += 1

                module["sections"].append(section)  # Добавляем раздел в модуль
                section_count += 1

            course_data["modules"].append(module)  # Добавляем модуль в курс
            module_count += 1

        # Сохраните данные в JSON файл
        with open('course_data.json', 'w', encoding='utf-8') as json_file:
            json.dump(course_data, json_file, ensure_ascii=False, indent=4)

        # Получите учителя по имени пользователя
        teacher = Teacher.objects.filter(name=request.user).first()
        if teacher is None:
            return JsonResponse({"error": "Учитель не найден."}, status=404)

        # Создайте курс
        course = Courses(
            teacher=teacher,
            name=course_data["title"],
            progress="0%",  # Укажите начальный прогресс
            author=teacher,  # Укажите имя автора
            language=course_data["title"],  # Укажите язык курса
            data=course_data  # Сохраните данные курса в формате JSON
        )
        course.save()

    return render(request, 'create_courses.html')


