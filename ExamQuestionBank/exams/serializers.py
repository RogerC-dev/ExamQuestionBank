from rest_framework import serializers
from .models import Exam, ExamResult, WrongQuestion
from question_bank.models import ExamQuestion, Question, Subject


class ExamResultSerializer(serializers.ModelSerializer):
    """考試結果序列化器"""
    exam_name = serializers.CharField(source='exam.name', read_only=True)

    class Meta:
        model = ExamResult
        fields = ['id', 'exam', 'exam_name', 'score', 'correct_count', 'total_count', 'duration_seconds', 'completed_at']
        read_only_fields = ['id', 'completed_at']


class ExamResultCreateSerializer(serializers.Serializer):
    """考試結果創建序列化器"""
    exam_id = serializers.IntegerField()
    score = serializers.IntegerField(min_value=0, max_value=100)
    correct_count = serializers.IntegerField(min_value=0)
    total_count = serializers.IntegerField(min_value=1)
    duration_seconds = serializers.IntegerField(required=False, min_value=0)
    wrong_question_ids = serializers.ListField(child=serializers.IntegerField(), required=False, default=[])


class WrongQuestionSerializer(serializers.ModelSerializer):
    """錯題序列化器"""
    question_content = serializers.CharField(source='question.content', read_only=True)
    question_subject = serializers.CharField(source='question.subject', read_only=True)
    is_in_flashcard = serializers.SerializerMethodField()
    is_bookmarked = serializers.SerializerMethodField()
    user_note = serializers.SerializerMethodField()

    class Meta:
        model = WrongQuestion
        fields = [
            'id', 'question', 'question_content', 'question_subject',
            'wrong_count', 'last_wrong_at', 'reviewed',
            'is_in_flashcard', 'is_bookmarked', 'user_note'
        ]
        read_only_fields = ['id', 'wrong_count', 'last_wrong_at']

    def get_is_in_flashcard(self, obj):
        """檢查此題目是否已被使用者加入快閃卡"""
        # 優先使用預查詢的資料（避免 N+1）
        flashcard_ids = self.context.get('flashcard_question_ids')
        if flashcard_ids is not None:
            return obj.question_id in flashcard_ids
        # Fallback: 單題查詢
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            return obj.question.flashcards.filter(user=request.user).exists()
        return False

    def get_is_bookmarked(self, obj):
        """檢查此題目是否已被使用者收藏"""
        # 優先使用預查詢的資料（避免 N+1）
        bookmark_ids = self.context.get('bookmark_question_ids')
        if bookmark_ids is not None:
            return obj.question_id in bookmark_ids
        # Fallback: 單題查詢
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            return obj.question.bookmarks.filter(user=request.user).exists()
        return False

    def get_user_note(self, obj):
        """取得使用者對此題目的筆記，若無則回傳 None"""
        # 優先使用預查詢的資料（避免 N+1）
        notes_dict = self.context.get('notes_dict')
        if notes_dict is not None:
            return notes_dict.get(obj.question_id)
        # Fallback: 單題查詢
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            note = obj.question.notes.filter(user=request.user).first()
            return note.content if note else None
        return None


class ExamListSerializer(serializers.ModelSerializer):
    """考卷列表序列化器"""
    question_count = serializers.SerializerMethodField()
    created_by_username = serializers.CharField(source='created_by.username', read_only=True, allow_null=True)
    is_owner = serializers.SerializerMethodField()

    class Meta:
        model = Exam
        fields = [
            'id', 'name', 'description', 'time_limit',
            'created_by', 'created_by_username', 'created_by_admin',
            'is_owner', 'created_at', 'updated_at', 'question_count'
        ]
        read_only_fields = ['id', 'created_by', 'created_by_username', 'created_at', 'updated_at']

    def get_question_count(self, obj):
        return obj.exam_questions.count()
    
    def get_is_owner(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.created_by == request.user or request.user.is_staff
        return False


class ExamQuestionSerializer(serializers.ModelSerializer):
    """考卷題目關聯序列化器"""
    question_content = serializers.CharField(source='question.content', read_only=True)
    question_subject = serializers.CharField(source='question.subject', read_only=True)
    question_category = serializers.CharField(source='question.category', read_only=True)

    class Meta:
        model = ExamQuestion
        fields = ['id', 'question', 'order', 'points', 'question_content', 'question_subject', 'question_category']
        read_only_fields = ['id']


class ExamDetailSerializer(serializers.ModelSerializer):
    """考卷詳細序列化器，包含所有題目"""
    exam_questions = ExamQuestionSerializer(many=True, read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True, allow_null=True)

    class Meta:
        model = Exam
        fields = [
            'id', 'name', 'description', 'time_limit',
            'created_by', 'created_by_username', 'created_by_admin',
            'created_at', 'updated_at', 'exam_questions'
        ]
        read_only_fields = ['id', 'created_by', 'created_by_username', 'created_at', 'updated_at']


class ExamCreateUpdateSerializer(serializers.ModelSerializer):
    """考卷創建和更新序列化器"""

    class Meta:
        model = Exam
        fields = ['name', 'description', 'time_limit']
        # created_by 不在 fields 中,由後端自動設定


class ExamQuestionCreateSerializer(serializers.ModelSerializer):
    """考卷題目關聯創建序列化器"""

    class Meta:
        model = ExamQuestion
        fields = ['question', 'order', 'points']

    def validate(self, data):
        # 檢查題目是否存在
        question_id = data.get('question')
        if question_id and not Question.objects.filter(id=question_id.id).exists():
            raise serializers.ValidationError({"question": "題目不存在"})
        return data
