from django import forms
from .models import StudentCourser, Courses

class SubCourses(forms.ModelForm):
    class Meta:
        model = StudentCourser
        fields = ['courses', 'student']

class CourseForm(forms.ModelForm):
    class Meta:
        model = Courses
        fields = ['data']