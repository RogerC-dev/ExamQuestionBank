from django.db import models
from users.models import User


class ExamSeries(models.Model):
    """考試別（如：司法官、律師）"""
    name = models.CharField(max_length=50, unique=True, verbose_name="考試別名稱")
    code = models.CharField(max_length=20, unique=True, verbose_name="代碼")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'exam_series'
        verbose_name = '考試別'
        verbose_name_plural = '考試別'

    def __str__(self):
        return self.name


class ExamSession(models.Model):
    """年度場次"""
    exam_series = models.ForeignKey(ExamSeries, on_delete=models.CASCADE, related_name='sessions')
    year = models.IntegerField(verbose_name="年度")
    session = models.CharField(max_length=20, verbose_name="場次", default="第一試")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'exam_session'
        verbose_name = '年度場次'
        verbose_name_plural = '年度場次'
        unique_together = [['exam_series', 'year', 'session']]

    def __str__(self):
        return f"{self.exam_series.name} {self.year}年 {self.session}"


class QuestionSet(models.Model):
    """題組"""
    exam_session = models.ForeignKey(ExamSession, on_delete=models.CASCADE, related_name='question_sets')
    subject = models.CharField(max_length=50, verbose_name="科目")
    question_type = models.CharField(max_length=20, verbose_name="題型", default="選擇題")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'question_set'
        verbose_name = '題組'
        verbose_name_plural = '題組'

    def __str__(self):
        return f"{self.exam_session} - {self.subject}"


class Tag(models.Model):
    """標籤（關鍵字、法條）"""
    name = models.CharField(max_length=100, unique=True, verbose_name="標籤名稱")
    category = models.CharField(max_length=50, verbose_name="分類", default="general")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'tag'
        verbose_name = '標籤'
        verbose_name_plural = '標籤'

    def __str__(self):
        return self.name


class Question(models.Model):
    """題目主體"""
    question_set = models.ForeignKey(QuestionSet, on_delete=models.CASCADE, related_name='questions', null=True, blank=True)
    content = models.TextField(verbose_name="題目內容")
    question_type = models.CharField(max_length=20, verbose_name="題型", default="選擇題")
    difficulty = models.CharField(max_length=20, verbose_name="難度", default="medium")
    explanation = models.TextField(blank=True, null=True, verbose_name="解析")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_questions')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tags = models.ManyToManyField(Tag, related_name='questions', blank=True)

    class Meta:
        db_table = 'question'
        verbose_name = '題目'
        verbose_name_plural = '題目'

    def __str__(self):
        return self.content[:50] + "..." if len(self.content) > 50 else self.content


class QuestionOption(models.Model):
    """題目選項"""
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options')
    content = models.TextField(verbose_name="選項內容")
    is_correct = models.BooleanField(default=False, verbose_name="是否為正確答案")
    order = models.IntegerField(default=0, verbose_name="順序")

    class Meta:
        db_table = 'question_option'
        verbose_name = '題目選項'
        verbose_name_plural = '題目選項'
        ordering = ['order']

    def __str__(self):
        return f"{self.question.id} - {self.content[:30]}"


class ExamQuestion(models.Model):
    """
    考卷-題目中介表
    """
    # ORM 關聯
    exam = models.ForeignKey('exams.Exam', on_delete=models.CASCADE, related_name='exam_questions', verbose_name="考卷")
    question = models.ForeignKey('Question', on_delete=models.CASCADE, related_name='exam_questions', verbose_name="題目")

    # 資料庫欄位
    order = models.IntegerField(verbose_name="題目順序")
    points = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="配分")

    class Meta:
        db_table = 'exam_question'
        verbose_name = '考卷題目'
        verbose_name_plural = '考卷題目'
        ordering = ['order']
        unique_together = [['exam', 'question'], ['exam', 'order']]

    def __str__(self):
        return f"{self.exam.name} - 題目{self.order}"


class Attempt(models.Model):
    """作答記錄"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attempts')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='attempts')
    selected_option = models.ForeignKey(QuestionOption, on_delete=models.SET_NULL, null=True, blank=True)
    is_correct = models.BooleanField(verbose_name="是否正確")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'attempt'
        verbose_name = '作答記錄'
        verbose_name_plural = '作答記錄'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.question.id}"


class Note(models.Model):
    """筆記"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notes')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='notes')
    content = models.TextField(verbose_name="筆記內容")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'note'
        verbose_name = '筆記'
        verbose_name_plural = '筆記'
        unique_together = [['user', 'question']]

    def __str__(self):
        return f"{self.user.username} - {self.question.id}"


class Bookmark(models.Model):
    """收藏"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookmarks')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='bookmarks')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'bookmark'
        verbose_name = '收藏'
        verbose_name_plural = '收藏'
        unique_together = [['user', 'question']]

    def __str__(self):
        return f"{self.user.username} - {self.question.id}"


class AIChatHistory(models.Model):
    """AI 聊天記錄"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_chat_history')
    message = models.TextField(verbose_name="使用者訊息")
    response = models.TextField(verbose_name="AI 回應")
    context_type = models.CharField(max_length=50, blank=True, null=True, verbose_name="上下文類型")
    context_id = models.IntegerField(blank=True, null=True, verbose_name="上下文ID")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ai_chat_history'
        verbose_name = 'AI 聊天記錄'
        verbose_name_plural = 'AI 聊天記錄'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.message[:30]}"
