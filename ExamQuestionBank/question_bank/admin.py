from django.contrib import admin

from .models import Question, AIChatHistory


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'subject', 'category', 'difficulty', 'status', 'created_at')
    list_filter = ('subject', 'category', 'difficulty', 'status')
    search_fields = ('content', 'subject', 'category')


@admin.register(AIChatHistory)
class AIChatHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'context_type', 'created_at')
    search_fields = ('user__username', 'message', 'response')
