from django.db import models
from django.contrib.auth.models import User


from Profile.models import Teacher, Student



class Courses(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=50)
    progress = models.CharField(max_length=50)
    author = models.CharField(max_length=50)
    language = models.CharField(max_length=30)

    def __str__(self):
        return str(self.name)

class StudentCourser(models.Model):
    courses = models.ForeignKey(Courses, on_delete=models.CASCADE, null=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return str(self.courses)

    class Meta:
        unique_together = ('courses', 'student')








