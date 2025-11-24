from django.db.models import Sum
from django.utils import timezone
from .models import Badge, UserBadge, UserXPLog, StudyGroupMembership, NotificationSchedule


class GamificationService:
    """Helper APIs for XP/badge computation."""

    @staticmethod
    def grant_xp(user, delta, source, metadata=None):
        log = UserXPLog.objects.create(user=user, delta=delta, source=source, metadata=metadata or {})
        return log

    @staticmethod
    def total_xp(user):
        result = UserXPLog.objects.filter(user=user).aggregate(total=Sum('delta'))
        return result['total'] or 0

    @staticmethod
    def check_badges(user):
        xp = GamificationService.total_xp(user)
        unlocked = []
        for badge in Badge.objects.all():
            if badge.threshold and xp >= badge.threshold:
                unlocked.append(GamificationService.award_badge(user, badge))
        return [b for b in unlocked if b]

    @staticmethod
    def award_badge(user, badge):
        user_badge, created = UserBadge.objects.get_or_create(user=user, badge=badge)
        return user_badge if created else None


class StudyGroupService:
    """Group membership helper methods."""

    @staticmethod
    def add_member(group, user, role='member'):
        return StudyGroupMembership.objects.get_or_create(group=group, user=user, defaults={'role': role})

    @staticmethod
    def remove_member(group, user):
        StudyGroupMembership.objects.filter(group=group, user=user).delete()


class NotificationService:
    """Basic scheduler for user reminders."""

    @staticmethod
    def schedule(user, title, payload, when, channel='in_app'):
        return NotificationSchedule.objects.create(
            user=user,
            title=title,
            payload=payload,
            scheduled_for=when,
            channel=channel,
        )

    @staticmethod
    def due_notifications(as_of=None):
        as_of = as_of or timezone.now()
        return NotificationSchedule.objects.filter(scheduled_for__lte=as_of, sent_at__isnull=True)

