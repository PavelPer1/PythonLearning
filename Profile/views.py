from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView
from django.views.generic import CreateView
from django.shortcuts import render, redirect

from .models import Teacher, Student
from .settings import *
from Profile.forms import RegisterForm, CreateUserForm
from Courses.models import Courses, StudentCourser

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import update_session_auth_hash
from .forms import ChangeUsernameForm, CustomPasswordChangeForm

@login_required
def settings_view(request):
    user = request.user

    if request.method == "POST":
        username_form = ChangeUsernameForm(request.POST, instance=user)
        password_form = CustomPasswordChangeForm(user, request.POST)

        if "change_username" in request.POST:
            if username_form.is_valid():
                current_password = username_form.cleaned_data["current_password"]
                if user.check_password(current_password):
                    username_form.save()
                    messages.success(request, "Логин успешно изменён!")
                    return redirect("settings")
                else:
                    messages.error(request, "Неверный текущий пароль!")
        elif "change_password" in request.POST:
            if password_form.is_valid():
                password_form.save()
                update_session_auth_hash(request, user)  # Чтобы не разлогинило
                messages.success(request, "Пароль успешно изменён!")
                return redirect("settings")

    else:
        username_form = ChangeUsernameForm(instance=user)
        password_form = CustomPasswordChangeForm(user)

    return render(
        request, "settings.html",
        {"username_form": username_form, "password_form": password_form}
    )


def help_view(request):
    return render(request, "help.html")



@login_required
def login_view(request):
    user = request.user  # Получаем текущего пользователя
    courses = Courses.objects.all()
    my_crs = []  # Список для курсов текущего пользователя
    # Получаем студента, связанного с текущим пользователем
    if  not Teacher.objects.filter(name=user).exists():
        student = Student.objects.get(name=user)
        # Получаем все объекты StudentCourser, связанные с этим студентом
        for student_course in StudentCourser.objects.filter(student=student):
            my_crs.append(student_course.courses)  # Добавляем курс в список
    else:
        teacher = Teacher.objects.get(name=user)
        # Получаем все объекты StudentCourser, связанные с этим студентом
        for teacher_course in Courses.objects.filter(teacher=teacher):
            my_crs.append(teacher_course)  # Добавляем курс в список

    teach = False

    if request.user.is_authenticated:
        teach = Teacher.objects.filter(name=request.user).exists()

    context = {
        'teacher': teach,
        'user': user,
        'courses': courses,
        'my_crs': my_crs
    }


    return render(request, 'profile_title/profile.html', context)

def logout_view(request):
    logout(request)
    return redirect('main_title')

class RegisterUser(CreateView):
    form_class = RegisterForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('login')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        return dict(list(context.items()))

    def form_valid(self, form):
        user = form.save()

        if self.request.POST.get('pointer') == 'teacher':
            a = Teacher(name=user)
            a.save()
        else:
            a = Student(name=user)
            a.save()
        login(self.request, user)
        return redirect('profile')


class LoginUser(LoginView):
    form_class = AuthenticationForm
    template_name = 'registration/login.html'
    success_url = reverse_lazy('profile')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        return dict(list(context.items()))