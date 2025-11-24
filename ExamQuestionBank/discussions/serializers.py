from rest_framework import serializers

from question_bank.models import Question
from .models import Discussion, DiscussionVote, ContentReport


class DiscussionSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    question_subject = serializers.CharField(source='question.subject', read_only=True)
    replies = serializers.SerializerMethodField()
    score = serializers.IntegerField(read_only=True)

    class Meta:
        model = Discussion
        fields = [
            'id',
            'question',
            'question_subject',
            'user',
            'user_name',
            'title',
            'content',
            'parent',
            'upvotes',
            'downvotes',
            'score',
            'status',
            'is_flagged',
            'created_at',
            'updated_at',
            'replies',
        ]
        read_only_fields = ['user', 'upvotes', 'downvotes', 'score', 'status', 'is_flagged', 'created_at', 'updated_at']

    def validate_question(self, value: Question):
        if not value:
            raise serializers.ValidationError('必須指定題目或將 parent 指向其他討論。')
        return value

    def get_replies(self, obj):
        children = obj.replies.order_by('created_at')
        return DiscussionSerializer(children, many=True, context=self.context).data


class DiscussionVoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscussionVote
        fields = ['vote_type']


class ContentReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentReport
        fields = ['reason', 'notes']

