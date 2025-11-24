from django.conf import settings
from django.db import models
from django.utils import timezone


class Discussion(models.Model):
    """Threaded discussion tied to a specific question or topic."""

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('locked', 'Locked'),
        ('hidden', 'Hidden'),
    ]

    question = models.ForeignKey('question_bank.Question', on_delete=models.CASCADE, related_name='discussions', null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='discussions')
    title = models.CharField(max_length=200)
    content = models.TextField()
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    upvotes = models.IntegerField(default=0)
    downvotes = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    is_flagged = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def score(self) -> int:
        return self.upvotes - self.downvotes


class DiscussionVote(models.Model):
    """Tracks user votes to prevent duplicates."""

    VOTE_TYPES = [
        ('up', 'Upvote'),
        ('down', 'Downvote'),
    ]

    discussion = models.ForeignKey(Discussion, on_delete=models.CASCADE, related_name='votes')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='discussion_votes')
    vote_type = models.CharField(max_length=4, choices=VOTE_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('discussion', 'user')

    def __str__(self):
        return f"{self.user} {self.vote_type} {self.discussion_id}"


class ContentReport(models.Model):
    """Content flag for moderation workflow."""

    discussion = models.ForeignKey(Discussion, on_delete=models.CASCADE, related_name='reports')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='discussion_reports')
    reason = models.CharField(max_length=255)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def mark_resolved(self):
        self.resolved_at = timezone.now()
        self.save(update_fields=['resolved_at'])
