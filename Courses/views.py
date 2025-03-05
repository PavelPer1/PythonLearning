from django.shortcuts import render, get_object_or_404
from Courses.models import StudentCourser, Courses
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required


import traceback
from io import StringIO
from contextlib import redirect_stdout
from Courses.models import Courses, StudentCourser


def course_list(request):
    courses = Courses.objects.all()  # Получаем все курсы
    return render(request, 'course_list.html', {'courses': courses})

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

    if request.method == "POST":
        code = request.POST.get('codearea', '')

        if len(code) > 1000:
            return HttpResponse("Code is too long", status=400)

        output = execute_code_safely(code)

    context = {
        'courses': course,
        'output': output,
        'code': code,
    }

    return render(request, 'get_courses.html', context)
