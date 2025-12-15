from django.conf import settings
from django.db import models


class StudyMetric(models.Model):
    """Aggregated study stats per user/subject."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='study_metrics')
    subject = models.ForeignKey('question_bank.Subject', on_delete=models.SET_NULL, null=True, blank=True)
    accuracy = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    total_attempts = models.IntegerField(default=0)
    correct_attempts = models.IntegerField(default=0)
    average_time = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'subject')


class Recommendation(models.Model):
    """Learning recommendation entries."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='recommendations')
    title = models.CharField(max_length=150)
    detail = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    seen = models.BooleanField(default=False)

