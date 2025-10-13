from rest_framework import serializers
from .models import ExamQuestion, Question, QuestionOption, Tag, Attempt, Note, Bookmark
from exams.models import Exam


class QuestionOptionSerializer(serializers.ModelSerializer):
    """題目選項序列化器"""
    class Meta:
        model = QuestionOption
        fields = ['id', 'content', 'is_correct']
        read_only_fields = ['id']


class TagSerializer(serializers.ModelSerializer):
    """標籤序列化器"""
    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']


class QuestionListSerializer(serializers.ModelSerializer):
    """簡化版Question序列化器，用於列表顯示"""
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = Question
        fields = [
            'content', 'status', 'created_at', 'created_by_username'
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
            'content', 'explanation', 'status', 'created_at', 'created_by_username',
            'options', 'tags'
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
            'explanation', 'status', 'options', 'tag_ids'
        ]
        read_only_fields = ['id']

    def create(self, validated_data):
        options_data = validated_data.pop('options', [])
        tag_ids = validated_data.pop('tag_ids', [])
        validated_data['created_by'] = self.context['request'].user

        question = Question.objects.create(**validated_data)

        # Create options
        for option_data in options_data:
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
            for option_data in options_data:
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
