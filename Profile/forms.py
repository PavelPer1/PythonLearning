from django.contrib.admin import forms
from django.contrib.auth.forms import UserCreationForm
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
        fields = ('email', 'number', 'fio')