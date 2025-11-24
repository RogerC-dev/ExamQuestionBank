from django.db.models import F
from .models import StudyMetric, Recommendation


class AnalyticsService:
    @staticmethod
    def record_attempt(user, subject, correct, duration):
        metric, _ = StudyMetric.objects.get_or_create(user=user, subject=subject)
        metric.total_attempts = F('total_attempts') + 1
        if correct:
            metric.correct_attempts = F('correct_attempts') + 1
        metric.average_time = duration  # placeholder
        metric.save()

    @staticmethod
    def recommend_focus(user, subject_name, reason):
        return Recommendation.objects.create(
            user=user,
            title=f'加強 {subject_name}',
            detail=reason,
        )

