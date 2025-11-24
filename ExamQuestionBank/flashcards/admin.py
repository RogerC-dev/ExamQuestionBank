from django.contrib import admin

from .models import Flashcard, FlashcardReviewLog


@admin.register(Flashcard)
class FlashcardAdmin(admin.ModelAdmin):
	list_display = ('id', 'user', 'question', 'status', 'next_review_date', 'review_count')
	list_filter = ('status', 'next_review_date')
	search_fields = ('user__username', 'question__content')
	autocomplete_fields = ('user', 'question')


@admin.register(FlashcardReviewLog)
class FlashcardReviewLogAdmin(admin.ModelAdmin):
	list_display = ('id', 'user', 'flashcard', 'rating', 'review_interval', 'reviewed_at')
	search_fields = ('user__username', 'flashcard__question__content')
	autocomplete_fields = ('user', 'flashcard')
