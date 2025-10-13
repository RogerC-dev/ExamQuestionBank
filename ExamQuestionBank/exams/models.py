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
