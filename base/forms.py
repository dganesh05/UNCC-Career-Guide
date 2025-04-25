from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

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