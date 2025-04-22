from django.shortcuts import render

def home(request):
    return render(request, 'home.html')  # Make sure you have a 'home.html' template

