from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now

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


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    major = models.CharField(max_length=100)
    graduation_year = models.IntegerField(null=True, blank=True)
    bio = models.TextField(blank=True)
    interests = models.TextField(blank=True)

    def __str__(self):
        return self.full_name


class Alumni(models.Model):
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

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(default=now)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"From {self.sender} to {self.recipient} at {self.timestamp}"

class ResourceOpportunity(models.Model):
    CATEGORY_CHOICES = [
        ('scholarships', 'Scholarships'),
        ('internships', 'Internships'),
        ('jobs', 'Jobs'),
        ('courses', 'Courses'),
        ('events', 'Events'),
    ]
    
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    link = models.URLField()
    deadline = models.DateField()

    def __str__(self):
        return self.title
    
class CareerStep(models.Model):
    role = models.CharField(max_length=100)
    next_role = models.CharField(max_length=100)
    avg_years = models.IntegerField()
    salary_range = models.CharField(max_length=100)
    skills_required = models.TextField()

    def __str__(self):
        return f"{self.role} → {self.next_role}"