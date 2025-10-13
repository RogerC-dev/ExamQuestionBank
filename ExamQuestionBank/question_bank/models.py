from django.db import models
from django.conf import settings


class ExamQuestion(models.Model):
    """
    考卷-題目中介表
    """
    # ORM 關聯
    exam = models.ForeignKey('exams.Exam', on_delete=models.CASCADE, related_name='exam_questions', verbose_name="考卷")
    question = models.ForeignKey('Question', on_delete=models.CASCADE, related_name='exam_questions', verbose_name="題目")

    # 資料庫欄位
    order = models.PositiveIntegerField(verbose_name="題目順序")
    points = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="配分")

    class Meta:
        db_table = 'exam_question'
        verbose_name = '考卷題目'
        verbose_name_plural = '考卷題目'
        ordering = ['order']
        unique_together = [['exam', 'question']]

    def __str__(self):
        return f"{self.exam.name} - 題目{self.order}"


class Question(models.Model):
    """
    題目
    """
    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('published', '已發布'),
    ]

    # ORM 關聯
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_questions', verbose_name="建立者")

    # 資料庫欄位
    subject = models.CharField(max_length=100, verbose_name="科目")
    category = models.CharField(max_length=50, verbose_name="題型分類")
    content = models.TextField(verbose_name="題目內容")
    explanation = models.TextField(blank=True, verbose_name="解析")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name="狀態")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="建立時間")

    class Meta:
        db_table = 'question'
        verbose_name = '題目'
        verbose_name_plural = '題目'
        indexes = [
            models.Index(fields=['subject']),
            models.Index(fields=['status']),
            models.Index(fields=['category']),
        ]

    def __str__(self):
        return f"{self.content[:50]}"


class QuestionOption(models.Model):
    """
    題目選項
    """
    # ORM 關聯
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options', verbose_name="題目")

    # 資料庫欄位
    content = models.TextField(verbose_name="選項內容")
    is_correct = models.BooleanField(default=False, verbose_name="是否為正確答案")

    class Meta:
        db_table = 'question_option'
        verbose_name = '題目選項'
        verbose_name_plural = '題目選項'

    def __str__(self):
        return f"{self.question.id} - {self.content[:30]}"


class Tag(models.Model):
    """
    標籤（關鍵字、法條等）
    """
    # 資料庫欄位
    name = models.CharField(max_length=100, unique=True, verbose_name="標籤名稱")

    # ORM 關聯（M2M 會自動建立中介表）
    questions = models.ManyToManyField(Question, related_name='tags', verbose_name="題目")

    class Meta:
        db_table = 'tag'
        verbose_name = '標籤'
        verbose_name_plural = '標籤'

    def __str__(self):
        return self.name


class Attempt(models.Model):
    """
    作答紀錄
    """
    # ORM 關聯
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='attempts', verbose_name="使用者")
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='attempts', verbose_name="題目")
    selected_options = models.ManyToManyField(QuestionOption, verbose_name="選擇的選項")

    # 資料庫欄位
    is_correct = models.BooleanField(verbose_name="是否正確")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作答時間")

    class Meta:
        db_table = 'attempt'
        verbose_name = '作答紀錄'
        verbose_name_plural = '作答紀錄'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - 題目{self.question.id}"


class Note(models.Model):
    """
    題目筆記
    """
    # ORM 關聯
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notes', verbose_name="使用者")
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='notes', verbose_name="題目")

    # 資料庫欄位
    content = models.TextField(verbose_name="筆記內容")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="建立時間")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新時間")

    class Meta:
        db_table = 'note'
        verbose_name = '筆記'
        verbose_name_plural = '筆記'
        unique_together = [['user', 'question']]

    def __str__(self):
        return f"{self.user.username} - 題目{self.question.id}"


class Bookmark(models.Model):
    """
    題目收藏
    """
    # ORM 關聯
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookmarks', verbose_name="使用者")
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='bookmarks', verbose_name="題目")

    # 資料庫欄位
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="收藏時間")

    class Meta:
        db_table = 'bookmark'
        verbose_name = '收藏'
        verbose_name_plural = '收藏'
        unique_together = [['user', 'question']]

    def __str__(self):
        return f"{self.user.username} - 題目{self.question.id}"
