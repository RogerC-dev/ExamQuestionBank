from rest_framework import serializers
from .models import Exam
from question_bank.models import ExamQuestion, Question


class ExamListSerializer(serializers.ModelSerializer):
    """考卷列表序列化器"""
    question_count = serializers.SerializerMethodField()

    class Meta:
        model = Exam
        fields = ['id', 'name', 'description', 'time_limit', 'created_at', 'updated_at', 'question_count']
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
        fields = ['id', 'name', 'description', 'time_limit', 'created_at', 'updated_at', 'exam_questions']
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
