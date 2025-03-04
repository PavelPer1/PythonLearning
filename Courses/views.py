from django.shortcuts import render, get_object_or_404
from Courses.models import StudentCourser, Courses
from django.http import HttpResponse

import traceback
from io import StringIO
from contextlib import redirect_stdout

def execute_code_safely(code):
    try:
        # Настроим безопасный контекст для exec
        local_globals = {
            '__builtins__': {
                'print': print,  # Ограничим доступ только к безопасному print
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
            '__name__': '__main__',  # Указываем, что это главный модуль
        }

        # Буфер для захвата вывода
        output_buffer = StringIO()

        # Перенаправляем stdout в буфер
        with redirect_stdout(output_buffer):
            # Выполнение кода в безопасной среде
            exec(code, local_globals)

        # Получаем вывод из буфера
        output = output_buffer.getvalue()

        # Если код не выводит ничего, то пытаемся вернуть последний результат выражения
        if not output:
            # Попробуем вернуть результат последнего выражения
            last_result = local_globals.get('_', None)
            if last_result is not None:
                output = str(last_result)

        return output if output else "Program executed without output."
    except Exception as e:
        # Возвращаем подробное сообщение об ошибке
        return f"Error: {str(e)}\n{traceback.format_exc()}"

# Вьюха для отображения текста задания и выполнения кода
def course_with_compiler(request, crs):
    # Получение курса
    course = get_object_or_404(Courses, name=crs)
    output = None  # Инициализируем output
    code = ""      # Инициализируем code

    if request.method == "POST":
        # Если POST-запрос, выполняем код из компилятора
        code = request.POST.get('codearea', '')

        # Ограничение длины кода
        if len(code) > 1000:  # Пример ограничения
            return HttpResponse("Code is too long", status=400)

        output = execute_code_safely(code)
    else:
        # Если GET-запрос, ничего не выполняем, только отображаем задание
        code = ""

    # Контекст для отображения курса и результата выполнения кода
    context = {
        'courses': course,
        'output': output,
        'code': code,
    }

    return render(request, 'get_courses.html', context)
