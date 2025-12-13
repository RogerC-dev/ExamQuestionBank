from django.db import models
from django.utils import timezone
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()


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
    subject = models.ForeignKey('Subject', on_delete=models.SET_NULL, null=True, blank=True, related_name='question_sets', verbose_name="科目")
    subject_name = models.CharField(max_length=50, blank=True, null=True, verbose_name="科目名稱（舊資料）")  # 保留舊資料
    question_type = models.CharField(max_length=20, verbose_name="題型", default="選擇題")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'question_set'
        verbose_name = '題組'
        verbose_name_plural = '題組'

    def __str__(self):
        subject_display = self.subject.name if self.subject else (self.subject_name or 'Unknown')
        return f"{self.exam_session} - {subject_display}"


class Tag(models.Model):
    """標籤（關鍵字、法條）"""
    name = models.CharField(max_length=100, unique=True, verbose_name="標籤名稱")
    category = models.CharField(max_length=50, verbose_name="分類", default="general")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'tag'
        verbose_name = '標籤'
        verbose_name_plural = '標籤'

    def __str__(self):
        return self.name


class Question(models.Model):
    """題目主體"""
    QUESTION_TYPE_CHOICES = [
        ('選擇題', '選擇題'),
        ('多選題', '多選題'),
        ('是非題', '是非題'),
        ('申論題', '申論題'),
    ]

    DIFFICULTY_CHOICES = [
        ('easy', '容易'),
        ('medium', '中等'),
        ('hard', '困難'),
    ]

    subject = models.CharField(max_length=100, verbose_name="科目")
    category = models.CharField(max_length=50, verbose_name="題型分類")
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPE_CHOICES, default='選擇題', verbose_name="題型")
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='medium', verbose_name="難度")
    status = models.CharField(max_length=20, choices=[('draft', '草稿'), ('published', '已發布')], default='draft', verbose_name="狀態")
    content = models.TextField(verbose_name="題目內容")
    explanation = models.TextField(blank=True, null=True, verbose_name="解析")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_questions')
    created_at = models.DateTimeField(auto_now_add=True)
    tags = models.ManyToManyField('Tag', through='QuestionTag', blank=True, related_name='questions', verbose_name="標籤")

    class Meta:
        db_table = 'question'
        verbose_name = '題目'
        verbose_name_plural = '題目'
        indexes = [
            models.Index(fields=['subject']),
            models.Index(fields=['question_type']),
            models.Index(fields=['difficulty']),
        ]

    def __str__(self):
        return self.content[:50] + "..." if len(self.content) > 50 else self.content


class QuestionTag(models.Model):
    """Question 與 Tag 之間的顯式中介表，方便後續擴充額外屬性。"""
    question = models.ForeignKey('Question', on_delete=models.CASCADE, verbose_name="題目")
    tag = models.ForeignKey('Tag', on_delete=models.CASCADE, verbose_name="標籤")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="建立時間")

    class Meta:
        db_table = 'question_tag'
        verbose_name = '題目標籤'
        verbose_name_plural = '題目標籤'
        unique_together = [['question', 'tag']]


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
    selected_options = models.ManyToManyField(QuestionOption, blank=True, related_name='attempts', verbose_name="選擇的選項")
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


class Subject(models.Model):
    """科目主表（標準化科目）"""
    name = models.CharField(max_length=100, unique=True, verbose_name="科目名稱")
    code = models.CharField(max_length=20, unique=True, verbose_name="科目代碼")
    category = models.CharField(max_length=50, verbose_name="分類", default="general")
    description = models.TextField(blank=True, null=True, verbose_name="說明")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'subject'
        verbose_name = '科目'
        verbose_name_plural = '科目'
        ordering = ['name']

    def __str__(self):
        return self.name


class EssayAnalysisChat(models.Model):
    """申論解析聊天記錄"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='essay_analysis_chats')
    question_text = models.TextField(verbose_name="申論題目")
    analysis_response = models.TextField(verbose_name="AI 解析回應")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'essay_analysis_chat'
        verbose_name = '申論解析記錄'
        verbose_name_plural = '申論解析記錄'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.question_text[:30]}"



class UserProgress(models.Model):
    """使用者學習進度追蹤"""
    MASTERY_LEVEL_CHOICES = [
        ('novice', '初學'),
        ('beginner', '入門'),
        ('intermediate', '中等'),
        ('advanced', '進階'),
        ('master', '精通'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_progress')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='user_progress')
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True, related_name='user_progress')
    exam_session = models.ForeignKey(ExamSession, on_delete=models.SET_NULL, null=True, blank=True, related_name='user_progress')
    is_correct = models.BooleanField(verbose_name="是否正確")
    time_spent = models.IntegerField(default=0, verbose_name="花費時間（秒）")
    attempt_count = models.IntegerField(default=1, verbose_name="嘗試次數")
    last_attempt_at = models.DateTimeField(auto_now=True, verbose_name="最後嘗試時間")
    mastery_level = models.CharField(max_length=20, choices=MASTERY_LEVEL_CHOICES, default='novice', verbose_name="熟練度")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_progress'
        verbose_name = '使用者進度'
        verbose_name_plural = '使用者進度'
        ordering = ['-last_attempt_at']
        indexes = [
            models.Index(fields=['user', 'subject']),
            models.Index(fields=['user', 'last_attempt_at']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.question.id} - {self.mastery_level}"


class StudySession(models.Model):
    """學習時段追蹤"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='study_sessions')
    started_at = models.DateTimeField(auto_now_add=True, verbose_name="開始時間")
    ended_at = models.DateTimeField(null=True, blank=True, verbose_name="結束時間")
    duration = models.IntegerField(default=0, verbose_name="持續時間（秒）")
    questions_attempted = models.IntegerField(default=0, verbose_name="答題數量")
    accuracy = models.DecimalField(max_digits=5, decimal_places=2, default=0.0, verbose_name="正確率")
    subjects_covered = models.ManyToManyField(Subject, related_name='study_sessions', blank=True)

    class Meta:
        db_table = 'study_session'
        verbose_name = '學習時段'
        verbose_name_plural = '學習時段'
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['user', 'started_at']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.started_at.strftime('%Y-%m-%d %H:%M')}"

    def end_session(self):
        """結束學習時段"""
        from django.utils import timezone
        self.ended_at = timezone.now()
        if self.started_at:
            delta = self.ended_at - self.started_at
            self.duration = int(delta.total_seconds())
        self.save()


class EssaySubmission(models.Model):
    """申論題提交"""
    STATUS_CHOICES = [
        ('pending', '待批改'),
        ('grading', '批改中'),
        ('completed', '已完成'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='essay_submissions')
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, related_name='essay_submissions')
    exam_year = models.IntegerField(verbose_name="考試年度")
    exam_session = models.ForeignKey(ExamSession, on_delete=models.SET_NULL, null=True, blank=True, related_name='essay_submissions')
    question_text = models.TextField(verbose_name="題目內容")
    answer_text = models.TextField(verbose_name="答案內容")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="狀態")
    submitted_at = models.DateTimeField(auto_now_add=True, verbose_name="提交時間")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'essay_submission'
        verbose_name = '申論題提交'
        verbose_name_plural = '申論題提交'
        ordering = ['-submitted_at']
        indexes = [
            models.Index(fields=['user', 'subject']),
            models.Index(fields=['user', 'submitted_at']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.subject.name if self.subject else 'Unknown'} - {self.submitted_at.strftime('%Y-%m-%d')}"


class EssayGrading(models.Model):
    """申論題批改結果"""
    GRADING_METHOD_CHOICES = [
        ('ai', 'AI 批改'),
        ('manual', '人工批改'),
    ]

    essay_submission = models.OneToOneField(EssaySubmission, on_delete=models.CASCADE, related_name='grading')
    score = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="得分")
    max_score = models.DecimalField(max_digits=5, decimal_places=2, default=100.0, verbose_name="滿分")
    feedback = models.TextField(verbose_name="總體評語")
    strengths = models.TextField(blank=True, null=True, verbose_name="優點")
    weaknesses = models.TextField(blank=True, null=True, verbose_name="缺點")
    suggestions = models.TextField(blank=True, null=True, verbose_name="改進建議")
    grading_method = models.CharField(max_length=20, choices=GRADING_METHOD_CHOICES, default='ai', verbose_name="批改方式")
    graded_at = models.DateTimeField(auto_now_add=True, verbose_name="批改時間")

    class Meta:
        db_table = 'essay_grading'
        verbose_name = '申論題批改'
        verbose_name_plural = '申論題批改'
        ordering = ['-graded_at']

    def __str__(self):
        return f"{self.essay_submission.user.username} - {self.score}/{self.max_score}"

    @property
    def percentage_score(self):
        """計算百分比分數"""
        if self.max_score > 0:
            return (self.score / self.max_score) * 100
        return 0


class StudyRecommendation(models.Model):
    """學習建議"""
    RECOMMENDATION_TYPE_CHOICES = [
        ('subject_focus', '科目重點'),
        ('weak_area', '弱項加強'),
        ('practice_schedule', '練習安排'),
        ('review_reminder', '複習提醒'),
        ('exam_prep', '考試準備'),
    ]

    PRIORITY_CHOICES = [
        ('low', '低'),
        ('medium', '中'),
        ('high', '高'),
        ('urgent', '緊急'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='study_recommendations')
    recommendation_type = models.CharField(max_length=30, choices=RECOMMENDATION_TYPE_CHOICES, verbose_name="建議類型")
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True, related_name='study_recommendations')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium', verbose_name="優先級")
    content = models.TextField(verbose_name="建議內容")
    generated_at = models.DateTimeField(auto_now_add=True, verbose_name="生成時間")
    is_read = models.BooleanField(default=False, verbose_name="已讀")
    read_at = models.DateTimeField(null=True, blank=True, verbose_name="閱讀時間")

    class Meta:
        db_table = 'study_recommendation'
        verbose_name = '學習建議'
        verbose_name_plural = '學習建議'
        ordering = ['-priority', '-generated_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['user', 'generated_at']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.get_recommendation_type_display()} - {self.get_priority_display()}"