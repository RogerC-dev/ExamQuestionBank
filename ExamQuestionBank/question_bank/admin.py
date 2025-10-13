from django.contrib import admin
from django.urls import path, include
from .models import Question
# Register your models here.
admin.site.register(Question)

