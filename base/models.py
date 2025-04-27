from django.db import models

# Create your models here.

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