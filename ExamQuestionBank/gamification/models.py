from django.conf import settings
from django.db import models


class Badge(models.Model):
    """Tracks available badges and their unlock criteria."""

    TRIGGER_CHOICES = [
        ("attempts", "Attempts completed"),
        ("streak", "Daily streak"),
        ("score", "Score threshold"),
        ("custom", "Custom condition"),
    ]

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=100, blank=True)
    trigger = models.CharField(max_length=20, choices=TRIGGER_CHOICES, default="attempts")
    threshold = models.IntegerField(default=0)
    xp_reward = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class UserBadge(models.Model):
    """Badges earned by a given user."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user_badges")
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE, related_name="awards")
    awarded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "badge")
        ordering = ["-awarded_at"]

    def __str__(self):
        return f"{self.user} -> {self.badge}"


class UserXPLog(models.Model):
    """Per-event XP deltas used to compute level progression."""

    SOURCE_CHOICES = [
        ("attempt", "Question attempt"),
        ("streak", "Study streak"),
        ("badge", "Badge bonus"),
        ("manual", "Manual grant"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="xp_logs")
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES)
    delta = models.IntegerField(default=0)
    metadata = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class StudyGroup(models.Model):
    """Collaborative group for study sessions and mock exams."""

    VISIBILITY_CHOICES = [
        ("private", "Private"),
        ("invite", "Invite only"),
        ("public", "Public"),
    ]

    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="owned_study_groups")
    visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default="private")
    max_members = models.IntegerField(default=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class StudyGroupMembership(models.Model):
    """Membership and roles within a study group."""

    ROLE_CHOICES = [
        ("member", "Member"),
        ("moderator", "Moderator"),
    ]

    group = models.ForeignKey(StudyGroup, on_delete=models.CASCADE, related_name="memberships")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="study_memberships")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="member")
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("group", "user")
        ordering = ["-joined_at"]


class NotificationSchedule(models.Model):
    """Scheduled reminders for study sessions, mock exams, etc."""

    CHANNEL_CHOICES = [
        ("email", "Email"),
        ("push", "Push"),
        ("in_app", "In-app"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    title = models.CharField(max_length=200)
    payload = models.JSONField()
    scheduled_for = models.DateTimeField()
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES, default="in_app")
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["scheduled_for"]

    @property
    def is_pending(self):
        return self.sent_at is None

