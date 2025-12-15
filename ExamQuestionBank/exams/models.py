from django.db import models
from django.conf import settings


class ExamResult(models.Model):
    """考試結果記錄"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='exam_results')
    exam = models.ForeignKey('Exam', on_delete=models.CASCADE, related_name='results')
    score = models.IntegerField(verbose_name="分數")
    correct_count = models.IntegerField(verbose_name="答對題數")
    total_count = models.IntegerField(verbose_name="總題數")
    duration_seconds = models.IntegerField(null=True, blank=True, verbose_name="作答時間(秒)")
    completed_at = models.DateTimeField(auto_now_add=True, verbose_name="完成時間")

    class Meta:
        db_table = 'exam_result'
        verbose_name = '考試結果'
        verbose_name_plural = '考試結果'
        ordering = ['-completed_at']

    def __str__(self):
        return f"{self.user.username} - {self.exam.name} - {self.score}分"


class WrongQuestion(models.Model):
    """錯題記錄"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wrong_questions')
    question = models.ForeignKey('question_bank.Question', on_delete=models.CASCADE, related_name='wrong_records')
    exam_result = models.ForeignKey(ExamResult, on_delete=models.CASCADE, related_name='wrong_questions', null=True)
    wrong_count = models.IntegerField(default=1, verbose_name="錯誤次數")
    last_wrong_at = models.DateTimeField(auto_now=True, verbose_name="最後錯誤時間")
    reviewed = models.BooleanField(default=False, verbose_name="已複習")

    class Meta:
        db_table = 'wrong_question'
        verbose_name = '錯題'
        verbose_name_plural = '錯題'
        unique_together = [['user', 'question']]
        ordering = ['-last_wrong_at']

    def __str__(self):
        return f"{self.user.username} - Q{self.question.id} - {self.wrong_count}次"


class Exam(models.Model):
    """
    考試/考卷
    """
    # 基本資訊
    name = models.CharField(max_length=200, verbose_name="考卷名稱")
    description = models.TextField(blank=True, verbose_name="考試說明")
    time_limit = models.IntegerField(null=True, blank=True, verbose_name="考試時間限制(分鐘)")
    
    # 建立者與權限
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_exams',
        verbose_name="建立者"
    )
    created_by_admin = models.BooleanField(default=False, verbose_name="是否為管理員建立")
    
    # 時間戳記
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="建立時間")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="修改時間")

    class Meta:
        db_table = 'exam'
        verbose_name = '考試'
        verbose_name_plural = '考試'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['created_by', 'created_at']),
        ]

    def __str__(self):
        return self.name
