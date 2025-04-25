from django.contrib import admin
from .models import Mentor
from .models import ChatMessage
from .models import Student
from .models import Alumni

admin.site.register(ChatMessage)
admin.site.register(Mentor)
admin.site.register(Student)
admin.site.register(Alumni)