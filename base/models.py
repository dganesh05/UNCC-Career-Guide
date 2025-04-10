from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Mentor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)


    full_name = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
    company = models.CharField(max_length=100)
    bio = models.TextField()
    expertise = models.CharField(max_length=255)
    education = models.TextField(blank=True)
    experience = models.TextField(blank=True)


    def __str__(self):
        return self.full_name
