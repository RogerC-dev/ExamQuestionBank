from django.contrib import admin
from .models import Discussion, DiscussionVote, ContentReport


@admin.register(Discussion)
class DiscussionAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'user', 'question', 'status', 'upvotes', 'downvotes', 'is_flagged', 'created_at')
    list_filter = ('status', 'is_flagged', 'created_at')
    search_fields = ('title', 'content', 'user__username')
    autocomplete_fields = ('question', 'user', 'parent')


@admin.register(DiscussionVote)
class DiscussionVoteAdmin(admin.ModelAdmin):
    list_display = ('id', 'discussion', 'user', 'vote_type', 'created_at')
    list_filter = ('vote_type', 'created_at')
    search_fields = ('discussion__title', 'user__username')


@admin.register(ContentReport)
class ContentReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'discussion', 'user', 'reason', 'created_at', 'resolved_at')
    list_filter = ('created_at', 'resolved_at')
    search_fields = ('discussion__title', 'user__username', 'reason')
