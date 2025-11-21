from django.db import models
from django.conf import settings


class Exam(models.Model):
    """
    考試/考卷
    """
    # 資料庫欄位
    name = models.CharField(max_length=200, verbose_name="考卷名稱")
    description = models.TextField(blank=True, verbose_name="考試說明")
    time_limit = models.IntegerField(null=True, blank=True, verbose_name="考試時間限制(分鐘)")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="建立時間")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="修改時間")

    class Meta:
        db_table = 'exam'
        verbose_name = '考試'
        verbose_name_plural = '考試'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class MockExam(models.Model):
    """AI 生成的模擬測驗"""
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='mock_exams')
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='mock_exams', null=True, blank=True)
    name = models.CharField(max_length=200, verbose_name="測驗名稱")
    subject = models.ForeignKey('question_bank.Subject', on_delete=models.SET_NULL, null=True, blank=True, related_name='mock_exams', verbose_name="科目")
    question_count = models.IntegerField(default=20, verbose_name="題目數量")
    time_limit = models.IntegerField(null=True, blank=True, verbose_name="時間限制（分鐘）")
    ai_generated = models.BooleanField(default=True, verbose_name="AI 生成")
    generated_at = models.DateTimeField(auto_now_add=True, verbose_name="生成時間")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'mock_exam'
        verbose_name = '模擬測驗'
        verbose_name_plural = '模擬測驗'
        ordering = ['-generated_at']
        indexes = [
            models.Index(fields=['user', 'generated_at']),
            models.Index(fields=['subject']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.name}"