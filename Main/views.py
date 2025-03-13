from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView

from django.shortcuts import render, redirect

from Profile.models import Teacher


def render_main_title(request):
    teach = False

    if request.user.is_authenticated:
        teach = Teacher.objects.filter(name=request.user).exists()

    context = {
        'teacher':teach
    }
    return render(request, 'index.html', context=context)
