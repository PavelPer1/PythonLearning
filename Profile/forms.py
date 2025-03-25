from django.contrib.admin import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.models import AbstractUser, User
from django import forms
from django.forms import ModelForm
from .models import *


class RegisterForm(UserCreationForm):

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')


class CreateUserForm(ModelForm):

    class Meta:
        model = Profile
        fields = ('email', 'number', 'fio', 'pointer')

class ChangeUsernameForm(forms.ModelForm):
    current_password = forms.CharField(widget=forms.PasswordInput, label="Текущий пароль")

    class Meta:
        model = User
        fields = ["username"]

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        if User.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
            self.add_error("username", "Этот логин уже занят!")
        return cleaned_data


class CustomPasswordChangeForm(PasswordChangeForm):
    pass  # Наследует всю логику смены пароля