from django import forms
from .models import StudentCourser

class SubCourses(forms.ModelForm):
    class Meta:
        model = StudentCourser
        fields = ['courses', 'student']