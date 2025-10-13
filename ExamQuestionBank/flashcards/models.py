from django.db import models
from django.conf import settings
from django.utils import timezone


class Flashcard(models.Model):
    """
    快閃卡
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='flashcards', verbose_name="使用者")
    question = models.ForeignKey('question_bank.Question', on_delete=models.CASCADE, related_name='flashcards', verbose_name="題目")
    next_review_date = models.DateField(default=timezone.now, verbose_name="下次複習日期")
    review_count = models.IntegerField(default=0, verbose_name="複習次數")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="建立時間")

    class Meta:
        db_table = 'flashcards'
        verbose_name = '快閃卡'
        verbose_name_plural = '快閃卡'
        unique_together = [['user', 'question']]
        ordering = ['next_review_date']

    def __str__(self):
        return f"{self.user.username} - 題目{self.question.id}"
