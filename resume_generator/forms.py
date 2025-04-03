from django import forms

class ResumeForm(forms.Form):
    name = forms.CharField(max_length=100)
    email = forms.EmailField()
    phone = forms.CharField(max_length=15)
    education = forms.CharField(widget=forms.Textarea, help_text="List your education details.")
    experience = forms.CharField(widget=forms.Textarea, help_text="List your work experience.")
    skills = forms.CharField(widget=forms.Textarea, help_text="List your skills.")
    career_goals = forms.CharField(widget=forms.Textarea, help_text="Describe your career goals.")