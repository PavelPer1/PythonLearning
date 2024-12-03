from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView
from django.views.generic import CreateView
from django.shortcuts import render, redirect

from .models import Teacher, Student
from .settings import *
from Profile.forms import RegisterForm, CreateUserForm


@login_required
def login_view(request):
    user = request.user  # Получаем текущего пользователя
    return render(request, 'profile_title/profile.html', {'user': user})

def logout_view(request):
    logout(request)
    return redirect('register')

class RegisterUser(CreateView):
    form_class = RegisterForm
    template_name = 'registration/registration.html'
    success_url = reverse_lazy('login')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        return dict(list(context.items()))

    def form_valid(self, form):
        user = form.save()

        if self.request.POST.get('pointer') == 'Учитель':
            a = Teacher(name=user)
            a.save()
        else:
            a = Student(name=user)
            a.save()
        login(self.request, user)
        return redirect('profile')
