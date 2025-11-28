from django.db import models
from django.conf import settings
from django.utils import timezone


class Flashcard(models.Model):
    """Spaced-repetition flashcard linked to a specific question."""

    STATUS_CHOICES = [
        ('learning', '學習中'),
        ('reviewing', '複習中'),
        ('mastered', '已掌握'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='flashcards', verbose_name="使用者")
    question = models.ForeignKey('question_bank.Question', on_delete=models.CASCADE, related_name='flashcards', verbose_name="題目")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='learning', verbose_name="狀態")
    ease_factor = models.FloatField(default=2.5, verbose_name="熟練因子")
    interval = models.IntegerField(default=1, verbose_name="間隔天數")
    repetition = models.IntegerField(default=0, verbose_name="連續成功次數")
    next_review_date = models.DateField(default=timezone.localdate, verbose_name="下次複習日期")
    last_reviewed_at = models.DateTimeField(null=True, blank=True, verbose_name="最後複習時間")
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

    @property
    def is_due(self) -> bool:
        """Return True when the flashcard should be reviewed today."""
        return self.next_review_date <= timezone.now().date()


class FlashcardReviewLog(models.Model):
    """History of each flashcard review for streak/stat analytics."""

    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]

    flashcard = models.ForeignKey(Flashcard, on_delete=models.CASCADE, related_name='review_logs', verbose_name="快閃卡")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='flashcard_reviews', verbose_name="使用者")
    rating = models.IntegerField(choices=RATING_CHOICES, verbose_name="表現評分")
    review_interval = models.IntegerField(default=1, verbose_name="複習間隔")
    reviewed_at = models.DateTimeField(auto_now_add=True, verbose_name="複習時間")

    class Meta:
        db_table = 'flashcard_review_logs'
        verbose_name = '快閃卡複習記錄'
        verbose_name_plural = '快閃卡複習記錄'
        ordering = ['-reviewed_at']

    def __str__(self):
        return f"{self.user.username} - 卡片{self.flashcard_id} - 評分{self.rating}"
