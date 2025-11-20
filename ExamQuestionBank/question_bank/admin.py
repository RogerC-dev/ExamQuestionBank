from django.contrib import admin
from django.urls import path, include
from .models import Question, AIChatHistory

# Register your models here.
admin.site.register(Question)
admin.site.register(AIChatHistory)

