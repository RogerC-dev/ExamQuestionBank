from rest_framework import serializers
from .models import (
    ExamQuestion, Question, QuestionOption, Tag, Attempt, Note, Bookmark,
    Subject, UserProgress, StudySession, EssaySubmission, EssayGrading, StudyRecommendation
)
from exams.models import Exam


class QuestionOptionSerializer(serializers.ModelSerializer):
    """題目選項序列化器"""
    class Meta:
        model = QuestionOption
        fields = ['id', 'content', 'is_correct', 'order']
        read_only_fields = ['id']


class TagSerializer(serializers.ModelSerializer):
    """標籤序列化器"""
    question_count = serializers.SerializerMethodField()

    class Meta:
        model = Tag
        fields = ['id', 'name', 'question_count', 'created_at']
        read_only_fields = ['id', 'question_count', 'created_at']

    def get_question_count(self, obj):
        return obj.questions.count()


class QuestionListSerializer(serializers.ModelSerializer):
    """簡化版Question序列化器，用於列表顯示"""
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = [
            'id', 'subject', 'category', 'question_type', 'difficulty', 'status', 'content', 'created_at', 'created_by_username', 'tags'
        ]
        read_only_fields = ['id', 'created_at']


class QuestionDetailSerializer(serializers.ModelSerializer):
    """完整Question序列化器，包含選項、標籤等"""
    options = QuestionOptionSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = Question
        fields = [
            'id', 'subject', 'category', 'question_type', 'difficulty', 'status', 'content', 'explanation',
            'created_at', 'created_by_username', 'options', 'tags'
        ]
        read_only_fields = ['id', 'created_at', 'created_by_username']


class QuestionCreateUpdateSerializer(serializers.ModelSerializer):
    """用於創建和更新Question"""
    options = QuestionOptionSerializer(many=True, required=False)
    tag_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        help_text="標籤 ID 列表"
    )

    class Meta:
        model = Question
        fields = [
            'subject', 'category', 'question_type', 'difficulty', 'status', 'content', 'explanation', 'options', 'tag_ids'
        ]
        read_only_fields = ['id']

    def create(self, validated_data):
        options_data = validated_data.pop('options', [])
        tag_ids = validated_data.pop('tag_ids', [])
        validated_data['created_by'] = self.context['request'].user

        question = Question.objects.create(**validated_data)

        # Create options
        for index, option_data in enumerate(options_data):
            # Ensure order is set based on the list index
            option_data['order'] = index
            QuestionOption.objects.create(question=question, **option_data)

        # Add tags
        if tag_ids:
            tags = Tag.objects.filter(id__in=tag_ids)
            question.tags.set(tags)

        return question

    def update(self, instance, validated_data):
        options_data = validated_data.pop('options', None)
        tag_ids = validated_data.pop('tag_ids', None)

        # Update question fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update options if provided
        if options_data is not None:
            instance.options.all().delete()
            for index, option_data in enumerate(options_data):
                # Ensure order is set based on the list index
                option_data['order'] = index
                QuestionOption.objects.create(question=instance, **option_data)

        # Update tags if provided
        if tag_ids is not None:
            tags = Tag.objects.filter(id__in=tag_ids)
            instance.tags.set(tags)

        return instance


class AttemptSerializer(serializers.ModelSerializer):
    """作答紀錄序列化器"""
    question_detail = QuestionDetailSerializer(source='question', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Attempt
        fields = [
            'id', 'user', 'username', 'question', 'selected_options',
            'is_correct', 'created_at', 'question_detail'
        ]
        read_only_fields = ['id', 'user', 'created_at']


class AttemptCreateSerializer(serializers.ModelSerializer):
    """創建作答紀錄的序列化器"""
    class Meta:
        model = Attempt
        fields = ['question', 'selected_options', 'is_correct']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        selected_options = validated_data.pop('selected_options', [])

        attempt = Attempt.objects.create(**validated_data)
        attempt.selected_options.set(selected_options)

        return attempt


class NoteSerializer(serializers.ModelSerializer):
    """筆記序列化器"""
    username = serializers.CharField(source='user.username', read_only=True)
    question_content = serializers.CharField(source='question.content', read_only=True)

    class Meta:
        model = Note
        fields = [
            'id', 'user', 'username', 'question', 'question_content',
            'content', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class BookmarkSerializer(serializers.ModelSerializer):
    """收藏序列化器"""
    question_detail = QuestionListSerializer(source='question', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Bookmark
        fields = ['id', 'user', 'username', 'question', 'created_at', 'question_detail']
        read_only_fields = ['id', 'user', 'created_at']


class SubjectSerializer(serializers.ModelSerializer):
    """科目序列化器"""
    class Meta:
        model = Subject
        fields = ['id', 'name', 'code', 'category', 'description', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserProgressSerializer(serializers.ModelSerializer):
    """使用者進度序列化器"""
    question_content = serializers.CharField(source='question.content', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = UserProgress
        fields = [
            'id', 'user', 'username', 'question', 'question_content',
            'subject', 'subject_name', 'exam_session', 'is_correct',
            'time_spent', 'attempt_count', 'last_attempt_at', 'mastery_level', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'last_attempt_at']


class StudySessionSerializer(serializers.ModelSerializer):
    """學習時段序列化器"""
    username = serializers.CharField(source='user.username', read_only=True)
    subjects_covered_names = serializers.SerializerMethodField()

    class Meta:
        model = StudySession
        fields = [
            'id', 'user', 'username', 'started_at', 'ended_at', 'duration',
            'questions_attempted', 'accuracy', 'subjects_covered', 'subjects_covered_names'
        ]
        read_only_fields = ['id', 'started_at']

    def get_subjects_covered_names(self, obj):
        return [s.name for s in obj.subjects_covered.all()]


class EssaySubmissionSerializer(serializers.ModelSerializer):
    """申論題提交序列化器"""
    username = serializers.CharField(source='user.username', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    grading = serializers.SerializerMethodField()

    class Meta:
        model = EssaySubmission
        fields = [
            'id', 'user', 'username', 'subject', 'subject_name', 'exam_year',
            'exam_session', 'question_text', 'answer_text', 'status',
            'submitted_at', 'updated_at', 'grading'
        ]
        read_only_fields = ['id', 'user', 'submitted_at', 'updated_at', 'status']

    def get_grading(self, obj):
        if hasattr(obj, 'grading'):
            return EssayGradingSerializer(obj.grading).data
        return None


class EssaySubmissionCreateSerializer(serializers.ModelSerializer):
    """申論題提交創建序列化器"""
    class Meta:
        model = EssaySubmission
        fields = [
            'subject', 'exam_year', 'exam_session', 'question_text', 'answer_text'
        ]

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        validated_data['status'] = 'pending'
        return super().create(validated_data)


class EssayGradingSerializer(serializers.ModelSerializer):
    """申論題批改序列化器"""
    percentage_score = serializers.ReadOnlyField()
    essay_submission_info = serializers.SerializerMethodField()

    class Meta:
        model = EssayGrading
        fields = [
            'id', 'essay_submission', 'essay_submission_info', 'score', 'max_score',
            'percentage_score', 'feedback', 'strengths', 'weaknesses', 'suggestions',
            'grading_method', 'graded_at'
        ]
        read_only_fields = ['id', 'graded_at']

    def get_essay_submission_info(self, obj):
        return {
            'id': obj.essay_submission.id,
            'subject': obj.essay_submission.subject.name if obj.essay_submission.subject else None,
            'exam_year': obj.essay_submission.exam_year
        }


class StudyRecommendationSerializer(serializers.ModelSerializer):
    """學習建議序列化器"""
    username = serializers.CharField(source='user.username', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)

    class Meta:
        model = StudyRecommendation
        fields = [
            'id', 'user', 'username', 'recommendation_type', 'subject', 'subject_name',
            'priority', 'content', 'generated_at', 'is_read', 'read_at'
        ]
        read_only_fields = ['id', 'generated_at']
