from django.db import models

# Create your models here.

class CareerConversation(models.Model):
    session_id = models.CharField(max_length=100)
    user_message = models.TextField()
    bot_response = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"Conversation {self.session_id} at {self.timestamp}"
