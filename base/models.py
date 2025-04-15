from django.db import models
from django.contrib.auth.models import User

class ChatMessage(models.Model):
    MESSAGE_TYPES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
    ]
    
    content = models.TextField()
    role = models.CharField(max_length=10, choices=MESSAGE_TYPES)
    timestamp = models.DateTimeField(auto_now_add=True)
    session_id = models.CharField(max_length=100)
    
    class Meta:
        ordering = ['timestamp']
    
    def __str__(self):
        return f"{self.role} - {self.timestamp}" 
    

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
