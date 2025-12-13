from rest_framework import serializers
from .models import Exam, MockExam, ExamResult, WrongQuestion
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

    class Meta:
        model = WrongQuestion
        fields = ['id', 'question', 'question_content', 'question_subject', 'wrong_count', 'last_wrong_at', 'reviewed']
        read_only_fields = ['id', 'wrong_count', 'last_wrong_at']


class ExamListSerializer(serializers.ModelSerializer):
    """考卷列表序列化器"""
    question_count = serializers.SerializerMethodField()

    class Meta:
        model = Exam
        fields = ['id', 'name', 'description', 'time_limit', 'created_by_admin', 'created_at', 'updated_at', 'question_count']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_question_count(self, obj):
        return obj.exam_questions.count()


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

    class Meta:
        model = Exam
        fields = ['id', 'name', 'description', 'time_limit', 'created_by_admin', 'created_at', 'updated_at', 'exam_questions']
        read_only_fields = ['id', 'created_at', 'updated_at']


class ExamCreateUpdateSerializer(serializers.ModelSerializer):
    """考卷創建和更新序列化器"""

    class Meta:
        model = Exam
        fields = ['name', 'description', 'time_limit']


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


class MockExamSerializer(serializers.ModelSerializer):
    """模擬測驗序列化器"""
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    exam = ExamDetailSerializer(read_only=True)

    class Meta:
        model = MockExam
        fields = [
            'id', 'name', 'subject', 'subject_name', 'question_count',
            'time_limit', 'ai_generated', 'generated_at', 'exam', 'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id', 'question_count', 'generated_at', 'created_at',
            'updated_at', 'ai_generated', 'exam'
        ]


class MockExamGenerateSerializer(serializers.Serializer):
    """模擬測驗生成請求序列化器"""
    name = serializers.CharField(required=False, allow_blank=True, max_length=200)
    subject_id = serializers.IntegerField(required=False)
    subject_name = serializers.CharField(required=False, allow_blank=True)
    topic = serializers.CharField(required=False, allow_blank=True)
    question_count = serializers.IntegerField(min_value=1, max_value=100, default=20)
    difficulty = serializers.ChoiceField(choices=['easy', 'medium', 'hard'], default='medium')
    exam_year = serializers.IntegerField(required=False)
    time_limit = serializers.IntegerField(required=False, min_value=5, max_value=600)
    reuse_question_bank = serializers.BooleanField(default=False)

    def validate(self, attrs):
        subject = None
        subject_id = attrs.get('subject_id')
        subject_name = attrs.get('subject_name')

        if subject_id:
            subject = Subject.objects.filter(id=subject_id).first()
            if not subject:
                raise serializers.ValidationError({'subject_id': '科目不存在'})
        elif subject_name:
            subject = Subject.objects.filter(name__iexact=subject_name.strip()).first()
            if not subject:
                raise serializers.ValidationError({'subject_name': '找不到指定科目'})
        else:
            raise serializers.ValidationError('必須提供 subject_id 或 subject_name')

        attrs['subject'] = subject

        if not attrs.get('name'):
            attrs['name'] = f"{subject.name} 模擬測驗"

        return attrs
