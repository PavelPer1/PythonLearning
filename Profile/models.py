from django.contrib.auth.models import User
from django.db import models

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    email = models.EmailField(max_length=250)
    number = models.CharField(max_length=50)
    fio = models.CharField(max_length=100, null=True)