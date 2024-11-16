from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView

from django.shortcuts import render, redirect


def render_main_title(request):
    return render(request, 'index.html')
