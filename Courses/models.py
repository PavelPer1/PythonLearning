from django.db import models
from django.contrib.auth.models import User


from Profile.models import Teacher, Student



class Courses(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=50)
    progress = models.CharField(max_length=50)
    author = models.CharField(max_length=50)
    language = models.CharField(max_length=30)
    data = models.JSONField(default=dict, null=True)
    image = models.ImageField(upload_to='course_covers/', null=True, blank=True)

    def __str__(self):
        return str(self.name)

class StudentCourser(models.Model):
    courses = models.ForeignKey(Courses, on_delete=models.CASCADE, null=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return str(self.courses)

    class Meta:
        unique_together = ('courses', 'student')


class CompletedTask(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True)
    course = models.ForeignKey(Courses, on_delete=models.CASCADE, null=True)
    task_id = models.CharField(max_length=255, null=True)
    code_solution = models.TextField(blank=True, null=True)
    completed_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        unique_together = ('student', 'course', 'task_id')
        verbose_name = 'Выполненное задание'
        verbose_name_plural = 'Выполненные задания'

    def __str__(self):
        return f"{self.student} - {self.course} - {self.task_id}"








