from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Mentor, Student, Alumni

ACCOUNT_TYPES = (
    ('student', 'Student'),
    ('mentor', 'Mentor'),
    ('alumni', 'Alumni'),
)

class CustomUserCreationForm(UserCreationForm):
    account_type = forms.ChoiceField(choices=ACCOUNT_TYPES, required=True)
    graduation_year = forms.IntegerField(required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'account_type', 'graduation_year']

class MentorForm(forms.ModelForm):
    class Meta:
        model = Mentor
        fields = ['full_name', 'title', 'company', 'bio', 'expertise', 'education', 'experience']

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['full_name', 'major', 'graduation_year', 'bio', 'interests']

class AlumniForm(forms.ModelForm):
    class Meta:
        model = Alumni
        fields = ['full_name', 'title', 'company', 'bio', 'expertise', 'education', 'experience']