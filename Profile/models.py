from django.contrib.auth.models import User
from django.db import models


class Student(models.Model):
    name = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return str(self.name)

class Teacher(models.Model):
    name = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return str(self.name)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    pointer = models.CharField(max_length=50, null=True)
    email = models.EmailField(max_length=250, null=True)
    number = models.CharField(max_length=50, null=True)
    fio = models.CharField(max_length=100, null=True)

    def __str__(self):
        return str(self.user.name)