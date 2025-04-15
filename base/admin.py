from django.contrib import admin
from .models import Mentor
from .models import ChatMessage

admin.site.register(ChatMessage)
admin.site.register(Mentor)