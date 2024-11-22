from django.shortcuts import render

from Courses.models import StudentCourser, Courses

import docker
import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import os





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

@require_POST
def compile(request):
  try:
    data = json.loads(request.body)
    code = data['code']

    # Настройка Docker-контейнера
    client = docker.from_env()
    container = client.containers.run(
      image='python:3.9', # Или другая подходящая версия Python
      command=['python', '-c', code],
      detach=True,
      auto_remove=True,
      mem_limit='128m', # Ограничение памяти
      cpu_shares=1024 #Ограничение CPU
    )

    #Получение результатов (это упрощенная реализация - нужно будет настроить)
    logs = container.logs(stream=True)
    output = ""
    for log in logs:
      output += log.decode()

    return JsonResponse({'result': output})

  except docker.errors.ContainerError as e:
    return JsonResponse({'error': f'Container error: {e}'})
  except docker.errors.ImageNotFound as e:
    return JsonResponse({'error': f'Image not found: {e}'})
  except Exception as e:
    return JsonResponse({'error': f'Error: {str(e)}'})

