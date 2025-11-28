from rest_framework import serializers
from django.utils import timezone

from question_bank.models import Question
from .models import Flashcard, FlashcardReviewLog


class FlashcardSerializer(serializers.ModelSerializer):
    question_subject = serializers.CharField(source='question.subject', read_only=True)
    question_content = serializers.CharField(source='question.content', read_only=True)
    question_difficulty = serializers.CharField(source='question.difficulty', read_only=True)
    is_due = serializers.SerializerMethodField()

    class Meta:
        model = Flashcard
        fields = [
            'id',
            'question',
            'question_subject',
            'question_content',
            'question_difficulty',
            'status',
            'ease_factor',
            'interval',
            'repetition',
            'next_review_date',
            'last_reviewed_at',
            'review_count',
            'is_due',
            'created_at',
        ]
        read_only_fields = [
            'status',
            'ease_factor',
            'interval',
            'repetition',
            'last_reviewed_at',
            'review_count',
            'is_due',
            'created_at',
        ]

    def validate_next_review_date(self, value):
        if isinstance(value, str):
            value = serializers.DateField().to_internal_value(value)
        if hasattr(value, 'date'):
            value = value.date()
        return value

    def validate_question(self, value: Question) -> Question:
        user = self.context['request'].user
        if Flashcard.objects.filter(user=user, question=value).exists():
            raise serializers.ValidationError('您已經為此題目建立快閃卡')
        return value

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        if 'next_review_date' not in validated_data:
            validated_data['next_review_date'] = timezone.localdate()
        return super().create(validated_data)

    def get_is_due(self, obj: Flashcard) -> bool:
        return obj.is_due


class FlashcardReviewSerializer(serializers.Serializer):
    rating = serializers.IntegerField(min_value=1, max_value=5)


class FlashcardReviewLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = FlashcardReviewLog
        fields = ['id', 'rating', 'review_interval', 'reviewed_at']
        read_only_fields = fields
